"""
Prompt Composer for building AI system prompts with personality bias injection.
Handles persona integration, safety overrides, and refusal logic.
"""

import logging
import re
from typing import Dict, Any, Optional, List

log = logging.getLogger("PromptComposer")


class PromptComposer:
    """
    Composes system prompts with personality bias, ensuring safety guardrails.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize prompt composer.
        
        Args:
            config: Full configuration dictionary including personality_bias
        """
        self.config = config
        self.personality_config = config.get("personality_bias", {})
        self.base_system_prompt = config.get("system_prompt", "")
        self.enabled = self.personality_config.get("enabled", 0)
        
        # Initialize telemetry (optional)
        self.telemetry = None
        try:
            from modules.persona_telemetry import get_telemetry
            self.telemetry = get_telemetry()
        except Exception as e:
            log.debug(f"Telemetry not available: {e}")
        
        log.info(f"PromptComposer initialized (enabled: {self.enabled})")
    
    def compose_prompt(self, tone_weights: Dict[str, float], 
                      stance_overrides: Dict[str, Any],
                      context: Optional[Dict[str, Any]] = None) -> str:
        """
        Compose the final system prompt with personality injection.
        
        Args:
            tone_weights: Current tone weight distribution
            stance_overrides: Topic-based stance overrides
            context: Optional context (user info, mood, etc.)
        
        Returns:
            Composed system prompt string
        """
        if not self.enabled:
            return self.base_system_prompt
        
        # Build persona description
        persona_text = self._build_persona_text(tone_weights, stance_overrides)
        
        # Build safety override text (highest priority)
        safety_text = self._build_safety_text()
        
        # Compose based on inject_mode
        inject_mode = self.personality_config.get("inject_mode", "prepend")
        
        if inject_mode == "prepend":
            composed = f"{persona_text}\n\n{self.base_system_prompt}"
        elif inject_mode == "append":
            composed = f"{self.base_system_prompt}\n\n{persona_text}"
        elif inject_mode == "replace":
            composed = persona_text
        else:
            log.warning(f"Unknown inject_mode: {inject_mode}, using prepend")
            composed = f"{persona_text}\n\n{self.base_system_prompt}"
        
        # Safety overrides always come last (highest priority)
        if safety_text:
            composed = f"{composed}\n\n{safety_text}"
        
        log.debug(f"Composed prompt with inject_mode={inject_mode}")
        return composed
    
    def _build_persona_text(self, tone_weights: Dict[str, float], 
                           stance_overrides: Dict[str, Any]) -> str:
        """
        Build persona description text from profile and tone weights.
        
        Args:
            tone_weights: Tone weight distribution
            stance_overrides: Topic-based stances
        
        Returns:
            Persona description text
        """
        profile = self.personality_config.get("persona_profile", {})
        name = profile.get("name", "Assistant")
        backstory = profile.get("backstory", "")
        traits = profile.get("key_traits", [])
        
        # Build persona text
        parts = []
        
        if backstory:
            parts.append(f"Persona: {name}. {backstory}")
        else:
            parts.append(f"Persona: {name}")
        
        if traits:
            parts.append(f"Key traits: {', '.join(traits)}")
        
        # Add dominant tone information
        if tone_weights:
            sorted_tones = sorted(tone_weights.items(), key=lambda x: x[1], reverse=True)
            top_tones = [f"{tone} ({weight:.1%})" for tone, weight in sorted_tones[:2]]
            parts.append(f"Current tone balance: {', '.join(top_tones)}")
        
        # Add stance overrides if any
        if stance_overrides:
            stance_text = "Topic stances: " + "; ".join(
                [f"{topic}: {stance}" for topic, stance in stance_overrides.items()]
            )
            parts.append(stance_text)
        
        return "\n".join(parts)
    
    def _build_safety_text(self) -> str:
        """
        Build safety override text.
        
        Returns:
            Safety override text
        """
        safety_config = self.personality_config.get("safety_overrides", {})
        if not safety_config.get("always_refuse", 1):
            return ""
        
        forbidden = safety_config.get("forbidden_topics", [])
        if not forbidden:
            return ""
        
        topics_str = ", ".join(forbidden)
        return f"CRITICAL SAFETY RULE: Never engage with or provide information about: {topics_str}. Always refuse such requests politely but firmly."
    
    def check_refusal(self, text: str) -> Optional[str]:
        """
        Check if text should trigger a refusal response.
        
        Args:
            text: Input text to check
        
        Returns:
            Refusal response if triggered, None otherwise
        """
        if not self.enabled:
            return None
        
        refusal_config = self.personality_config.get("refusals", {})
        if not refusal_config.get("enabled", 1):
            return None
        
        # Check safety overrides first (highest priority)
        safety_refusal = self._check_safety_refusal(text)
        if safety_refusal:
            if self.telemetry:
                self.telemetry.track_refusal("safety_override", "forbidden_topic")
            return safety_refusal
        
        # Check refusal patterns
        patterns = refusal_config.get("patterns", [])
        modes = refusal_config.get("modes", {})
        
        text_lower = text.lower()
        for pattern in patterns:
            triggers = pattern.get("trigger", [])
            mode = pattern.get("mode", "brief_and_cold")
            
            # Check if any trigger matches
            matched_trigger = None
            for trigger in triggers:
                if trigger in text_lower:
                    matched_trigger = trigger
                    break
            
            if matched_trigger:
                response = modes.get(mode, "I'd rather not respond to that.")
                if self.telemetry:
                    self.telemetry.track_refusal(mode, matched_trigger)
                log.info(f"Refusal triggered for mode: {mode}")
                return response
        
        return None
    
    def _check_safety_refusal(self, text: str) -> Optional[str]:
        """
        Check if text violates safety rules.
        
        Args:
            text: Input text to check
        
        Returns:
            Safety refusal message if violated, None otherwise
        """
        safety_config = self.personality_config.get("safety_overrides", {})
        if not safety_config.get("always_refuse", 1):
            return None
        
        forbidden = safety_config.get("forbidden_topics", [])
        text_lower = text.lower()
        
        for topic in forbidden:
            # Simple keyword matching (can be enhanced with more sophisticated methods)
            if topic.lower() in text_lower:
                log.warning(f"Safety violation detected: {topic}")
                return "I cannot engage with that topic. Let's discuss something else."
        
        return None
    
    def get_persona_summary(self, tone_weights: Dict[str, float], 
                          stance_overrides: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get a summary of the current persona state.
        
        Args:
            tone_weights: Current tone weights
            stance_overrides: Current stance overrides
        
        Returns:
            Persona summary dictionary
        """
        profile = self.personality_config.get("persona_profile", {})
        
        # Find dominant tone
        dominant_tone = "neutral"
        if tone_weights:
            dominant_tone = max(tone_weights.items(), key=lambda x: x[1])[0]
        
        return {
            "enabled": self.enabled,
            "name": profile.get("name", "Assistant"),
            "backstory": profile.get("backstory", ""),
            "traits": profile.get("key_traits", []),
            "dominant_tone": dominant_tone,
            "tone_weights": tone_weights,
            "stance_overrides": stance_overrides,
            "inject_mode": self.personality_config.get("inject_mode", "prepend")
        }
