"""
Persona State Store for managing personality evolution and persistence.
Supports session and user-scoped personas with volatility drift and evolution rules.
"""

import json
import logging
import random
import sqlite3
import time
from typing import Dict, Any, Optional, List, Tuple
from copy import deepcopy

log = logging.getLogger("PersonaStateStore")


class PersonaStateStore:
    """
    Manages persona state persistence with support for drift, evolution, and determinism.
    """
    
    def __init__(self, config: Dict[str, Any], db_path: str = "./persona_state.db"):
        """
        Initialize persona state store.
        
        Args:
            config: Personality bias configuration dictionary
            db_path: Path to SQLite database file
        """
        self.config = config
        self.db_path = db_path
        self.seed = config.get("persistence", {}).get("seed")
        self.scope = config.get("persistence", {}).get("scope", "session")
        
        # Initialize random seed for determinism if provided
        if self.seed is not None:
            random.seed(self.seed)
            log.info(f"Initialized with deterministic seed: {self.seed}")
        
        self._init_database()
        log.info(f"PersonaStateStore initialized (scope: {self.scope}, db: {db_path})")
    
    def _init_database(self) -> None:
        """Create database table if it doesn't exist."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS persona_states (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scope_type TEXT NOT NULL,
                    scope_id TEXT NOT NULL,
                    tone_weights TEXT NOT NULL,
                    stance_overrides TEXT,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(scope_type, scope_id)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS persona_evolution_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scope_type TEXT NOT NULL,
                    scope_id TEXT NOT NULL,
                    trigger TEXT NOT NULL,
                    magnitude REAL NOT NULL,
                    target_tone TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            conn.close()
            log.debug("Persona state database initialized")
        except Exception as e:
            log.error(f"Failed to initialize persona state database: {e}")
            raise
    
    def get_state(self, scope_id: str = "default") -> Dict[str, Any]:
        """
        Load persona state for the given scope.
        
        Args:
            scope_id: Scope identifier (user_id or session_id)
        
        Returns:
            Persona state dictionary with tone_weights and stance_overrides
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT tone_weights, stance_overrides FROM persona_states WHERE scope_type = ? AND scope_id = ?",
                (self.scope, scope_id)
            )
            result = cursor.fetchone()
            conn.close()
            
            if result:
                tone_weights = json.loads(result[0])
                stance_overrides = json.loads(result[1]) if result[1] else {}
                log.debug(f"Loaded persona state for {self.scope}:{scope_id}")
                return {"tone_weights": tone_weights, "stance_overrides": stance_overrides}
            else:
                # Return default state from config
                default_state = {
                    "tone_weights": deepcopy(self.config.get("tone_weights", {})),
                    "stance_overrides": deepcopy(self.config.get("stance_overrides", {}))
                }
                log.debug(f"No saved state for {self.scope}:{scope_id}, using defaults")
                return default_state
        except Exception as e:
            log.error(f"Failed to load persona state: {e}")
            return {
                "tone_weights": deepcopy(self.config.get("tone_weights", {})),
                "stance_overrides": deepcopy(self.config.get("stance_overrides", {}))
            }
    
    def save_state(self, scope_id: str, tone_weights: Dict[str, float], 
                   stance_overrides: Dict[str, Any]) -> None:
        """
        Save persona state for the given scope.
        
        Args:
            scope_id: Scope identifier (user_id or session_id)
            tone_weights: Current tone weight distribution
            stance_overrides: Current stance override mappings
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO persona_states (scope_type, scope_id, tone_weights, stance_overrides, last_updated)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                self.scope,
                scope_id,
                json.dumps(tone_weights),
                json.dumps(stance_overrides)
            ))
            conn.commit()
            conn.close()
            log.debug(f"Saved persona state for {self.scope}:{scope_id}")
        except Exception as e:
            log.error(f"Failed to save persona state: {e}")
    
    def apply_drift(self, tone_weights: Dict[str, float], volatility: float) -> Dict[str, float]:
        """
        Apply random drift to tone weights based on volatility.
        
        Args:
            tone_weights: Current tone weight distribution
            volatility: Drift rate (0.0 to 1.0)
        
        Returns:
            Drifted tone weights (normalized)
        """
        if volatility <= 0:
            return tone_weights
        
        drifted = {}
        for tone, weight in tone_weights.items():
            # Apply random drift
            drift = random.gauss(0, volatility)
            drifted[tone] = max(0.0, weight + drift)
        
        # Normalize to sum to 1.0
        total = sum(drifted.values())
        if total > 0:
            drifted = {k: v / total for k, v in drifted.items()}
        
        log.debug(f"Applied drift with volatility {volatility}")
        return drifted
    
    def apply_evolution(self, scope_id: str, trigger: str, 
                       tone_weights: Dict[str, float]) -> Dict[str, float]:
        """
        Apply evolution rule to tone weights based on trigger.
        
        Args:
            scope_id: Scope identifier
            trigger: Evolution trigger name
            tone_weights: Current tone weight distribution
        
        Returns:
            Evolved tone weights (clamped and normalized)
        """
        evolution_config = self.config.get("evolution_rules", {})
        if not evolution_config.get("enabled", 1):
            return tone_weights
        
        triggers = evolution_config.get("triggers", {})
        if trigger not in triggers:
            log.debug(f"No evolution rule for trigger: {trigger}")
            return tone_weights
        
        rule = triggers[trigger]
        magnitude = rule.get("magnitude", 0.0)
        target_tone = rule.get("target_tone")
        
        if not target_tone or target_tone not in tone_weights:
            return tone_weights
        
        # Apply evolution: increase target tone, decrease others proportionally
        evolved = deepcopy(tone_weights)
        evolved[target_tone] = min(1.0, evolved[target_tone] + magnitude)
        
        # Normalize
        total = sum(evolved.values())
        if total > 0:
            evolved = {k: v / total for k, v in evolved.items()}
        
        # Apply clamps
        clamps = evolution_config.get("clamps", {})
        for tone, weight in evolved.items():
            if tone in clamps:
                min_val, max_val = clamps[tone]
                evolved[tone] = max(min_val, min(max_val, weight))
        
        # Re-normalize after clamping
        total = sum(evolved.values())
        if total > 0:
            evolved = {k: v / total for k, v in evolved.items()}
        
        # Log evolution event
        self._log_evolution(scope_id, trigger, magnitude, target_tone)
        
        log.debug(f"Applied evolution for trigger '{trigger}': {target_tone} +{magnitude}")
        return evolved
    
    def _log_evolution(self, scope_id: str, trigger: str, magnitude: float, 
                      target_tone: str) -> None:
        """Log evolution event to database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO persona_evolution_log (scope_type, scope_id, trigger, magnitude, target_tone)
                VALUES (?, ?, ?, ?, ?)
            """, (self.scope, scope_id, trigger, magnitude, target_tone))
            conn.commit()
            conn.close()
        except Exception as e:
            log.warning(f"Failed to log evolution event: {e}")
    
    def reset_state(self, scope_id: str = "default") -> None:
        """
        Reset persona state to defaults for the given scope.
        
        Args:
            scope_id: Scope identifier to reset
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM persona_states WHERE scope_type = ? AND scope_id = ?",
                (self.scope, scope_id)
            )
            conn.commit()
            conn.close()
            log.info(f"Reset persona state for {self.scope}:{scope_id}")
        except Exception as e:
            log.error(f"Failed to reset persona state: {e}")
    
    def get_evolution_history(self, scope_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get evolution history for a scope.
        
        Args:
            scope_id: Scope identifier
            limit: Maximum number of events to return
        
        Returns:
            List of evolution events
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT trigger, magnitude, target_tone, timestamp 
                FROM persona_evolution_log 
                WHERE scope_type = ? AND scope_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (self.scope, scope_id, limit))
            results = cursor.fetchall()
            conn.close()
            
            return [
                {
                    "trigger": r[0],
                    "magnitude": r[1],
                    "target_tone": r[2],
                    "timestamp": r[3]
                }
                for r in results
            ]
        except Exception as e:
            log.error(f"Failed to get evolution history: {e}")
            return []
