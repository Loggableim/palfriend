"""
GUI module for configuration and monitoring interface.
"""

import asyncio
import logging
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Dict, Any, Optional

import sounddevice as sd

from settings import save_settings

log = logging.getLogger("ChatPalBrain")


class ScrollableFrame(ttk.Frame):
    """
    A scrollable frame widget for containing many configuration options.
    """
    
    def __init__(self, parent, *args, **kwargs) -> None:
        """
        Initialize scrollable frame.
        
        Args:
            parent: Parent widget
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
        """
        super().__init__(parent, *args, **kwargs)
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        self.vscroll = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vscroll.set)
        self.inner = ttk.Frame(self.canvas)
        self.inner.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.window_id = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.vscroll.grid(row=0, column=1, sticky="ns")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        def _on_resize(event):
            self.canvas.itemconfig(self.window_id, width=event.width)
        
        self.canvas.bind("<Configure>", _on_resize)
        
        def _on_mousewheel(event):
            delta = 0
            if getattr(event, 'num', None) == 4:
                delta = -1
            elif getattr(event, 'num', None) == 5:
                delta = 1
            elif getattr(event, 'delta', 0):
                delta = -1 if event.delta > 0 else 1
            self.canvas.yview_scroll(delta, "units")
        
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        self.canvas.bind_all("<Button-4>", _on_mousewheel)
        self.canvas.bind_all("<Button-5>", _on_mousewheel)


class GUIHandler(logging.Handler):
    """
    Custom logging handler that outputs to a text widget.
    """
    
    def __init__(self, text_widget: scrolledtext.ScrolledText) -> None:
        """
        Initialize GUI logging handler.
        
        Args:
            text_widget: Text widget to write logs to
        """
        super().__init__()
        self.text_widget = text_widget
    
    def emit(self, record: logging.LogRecord) -> None:
        """
        Emit a log record to the text widget.
        
        Args:
            record: Log record to emit
        """
        try:
            msg = self.format(record)
            self.text_widget.insert(tk.END, msg + "\n")
            self.text_widget.see(tk.END)
        except Exception:
            pass


class ConfigGUI(tk.Tk):
    """
    Main configuration GUI window.
    """
    
    def __init__(self, cfg: Dict[str, Any], start_callback) -> None:
        """
        Initialize configuration GUI.
        
        Args:
            cfg: Configuration dictionary
            start_callback: Callback to start the application
        """
        super().__init__()
        self.title("TikTok → Animaze ChatPal Brain")
        self.geometry("980x720")
        self.minsize(820, 560)
        self.cfg = cfg
        self.start_callback = start_callback
        self.micmon_ref = None
        
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Scrollable configuration area
        self.scroll = ScrollableFrame(self)
        self.scroll.grid(row=0, column=0, sticky="nsew", padx=12, pady=(12, 6))
        frm = self.scroll.inner
        
        # Configuration entries
        entries = [
            ("TikTok Handle", "tiktok", "unique_id"),
            ("TikTok Session ID (optional)", "tiktok", "session_id"),
            ("Animaze Host", "animaze", "host"),
            ("Animaze Port", "animaze", "port"),
            ("OpenAI API Key", "openai", "api_key"),
            ("OpenAI Model", "openai", "model"),
            ("Max Line Length", "style", "max_line_length"),
            ("Comment Enabled (0/1)", "comment", "enabled"),
            ("Comment Global Cooldown (s)", "comment", "global_cooldown"),
            ("Comment Per-User Cooldown (s)", "comment", "per_user_cooldown"),
            ("Comment Min Length", "comment", "min_length"),
            ("Max Replies Per Minute", "comment", "max_replies_per_min"),
            ("Reply Threshold (0..1)", "comment", "reply_threshold"),
            ("Respond to Greetings (0/1)", "comment", "respond_to_greetings"),
            ("Greeting Cooldown (s)", "comment", "greeting_cooldown"),
            ("Respond to Thanks (0/1)", "comment", "respond_to_thanks"),
            ("Ignore if startswith (csv)", "comment", "ignore_if_startswith"),
            ("Ignore if contains (csv)", "comment", "ignore_contains"),
            ("De-dupe TTL (s)", None, "dedupe_ttl"),
            ("Mic Enabled (0/1)", "microphone", "enabled"),
            ("Mic Device (Name oder Index)", "microphone", "device"),
            ("Mic Silence Threshold (RMS 0..1)", "microphone", "silence_threshold"),
            ("Mic Attack (ms)", "microphone", "attack_ms"),
            ("Mic Release (ms)", "microphone", "release_ms"),
            ("Flush Delay (ms)", "microphone", "flush_delay_ms"),
            ("Join: Enabled (0/1)", "join_rules", "enabled"),
            ("Join: Greet after seconds", "join_rules", "greet_after_seconds"),
            ("Join: Active TTL seconds", "join_rules", "active_ttl_seconds"),
            ("Join: Min idle since last output (s)", "join_rules", "min_idle_since_last_output_sec"),
            ("Join: Global welcome cooldown (s)", "join_rules", "greet_global_cooldown_sec"),
            ("Outbox: Window (s)", "outbox", "window_seconds"),
            ("Outbox: Max Items", "outbox", "max_items"),
            ("Outbox: Max Chars", "outbox", "max_chars"),
            ("Outbox: Separator", "outbox", "separator"),
            ("Speech: Wait start (ms)", "speech", "wait_start_timeout_ms"),
            ("Speech: Max speech (ms)", "speech", "max_speech_ms"),
            ("Speech: Post gap (ms)", "speech", "post_gap_ms")
        ]
        
        self.vars = {}
        for i, (label, sec, key) in enumerate(entries):
            ttk.Label(frm, text=f"{label}:").grid(row=i, column=0, sticky="w", pady=3, padx=(2, 8))
            val = self._get_val(sec, key)
            if isinstance(val, list):
                val = ",".join(map(str, val))
            var = tk.StringVar(value=str(val))
            self.vars[(sec, key)] = var
            ttk.Entry(frm, textvariable=var, width=56).grid(row=i, column=1, pady=3, sticky="ew")
        
        # Device selection
        dev_row = len(entries) + 1
        ttk.Label(frm, text="Input-Gerät wählen:").grid(row=dev_row, column=0, sticky="w", pady=(10, 3))
        try:
            devices = sd.query_devices()
            self.input_devs = [
                f"{i}: {d['name']}"
                for i, d in enumerate(devices)
                if (d.get('max_input_channels') or 0) > 0
            ]
        except Exception:
            self.input_devs = []
        
        self.dev_combo_var = tk.StringVar(
            value=self.input_devs[0] if self.input_devs else "Keine Eingänge gefunden"
        )
        self.dev_combo = ttk.Combobox(
            frm,
            textvariable=self.dev_combo_var,
            values=self.input_devs,
            state="readonly",
            width=56
        )
        self.dev_combo.grid(row=dev_row, column=1, sticky="ew", pady=(10, 3))
        
        # Device buttons
        btns = ttk.Frame(frm)
        btns.grid(row=dev_row + 1, column=1, sticky="w", pady=(0, 6))
        ttk.Button(
            btns,
            text="Als Mic Device übernehmen",
            command=self.apply_selected_device_to_cfg
        ).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(
            btns,
            text="Laufend wechseln (ohne Neustart)",
            command=self.switch_device_live
        ).grid(row=0, column=1)
        
        # VU meter
        vu_row = dev_row + 2
        ttk.Label(frm, text="Mic Level (VU):").grid(row=vu_row, column=0, sticky="w", pady=(8, 3))
        self.vu = ttk.Progressbar(frm, orient="horizontal", mode="determinate", length=380, maximum=1.0)
        self.vu.grid(row=vu_row, column=1, sticky="ew", pady=(8, 3))
        
        frm.columnconfigure(1, weight=1)
        
        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 6))
        btn_frame.columnconfigure(0, weight=1)
        ttk.Button(btn_frame, text="Save & Start", command=self.on_save).grid(
            row=0, column=0, padx=5, sticky="w"
        )
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).grid(
            row=0, column=1, padx=5, sticky="w"
        )
        
        # Log area
        self.log_text = scrolledtext.ScrolledText(self, wrap=tk.WORD)
        self.log_text.grid(row=2, column=0, sticky="nsew", padx=12, pady=(0, 12))
        self.log_text.configure(height=12)
        logging.getLogger().addHandler(GUIHandler(self.log_text))
        
        self.after(60, self._update_vu)
    
    def _update_vu(self) -> None:
        """Update VU meter display."""
        try:
            if self.micmon_ref:
                self.vu["value"] = float(self.micmon_ref.level)
            else:
                self.vu["value"] = 0.0
        except Exception:
            self.vu["value"] = 0.0
        self.after(60, self._update_vu)
    
    def apply_selected_device_to_cfg(self) -> None:
        """Apply selected device to configuration."""
        sel = self.dev_combo_var.get()
        if ":" in sel:
            idx = sel.split(":")[0].strip()
        else:
            idx = sel.strip()
        
        if ("microphone", "device") in self.vars:
            self.vars[("microphone", "device")].set(idx)
        
        self.cfg.setdefault("microphone", {})["device"] = idx
        save_settings(self.cfg)
    
    def switch_device_live(self) -> None:
        """Switch microphone device without restart."""
        sel = self.dev_combo_var.get()
        if not sel or ":" not in sel:
            messagebox.showerror("Fehler", "Kein gültiges Eingabegerät gewählt.")
            return
        
        idx = sel.split(":")[0].strip()
        
        if not self.micmon_ref:
            messagebox.showerror("Fehler", "Mic-Monitor läuft noch nicht.")
            return
        
        self.micmon_ref.set_device(idx)
        
        if ("microphone", "device") in self.vars:
            self.vars[("microphone", "device")].set(idx)
        
        self.cfg.setdefault("microphone", {})["device"] = idx
        save_settings(self.cfg)
    
    def _get_val(self, sec: Optional[str], key: str) -> Any:
        """
        Get configuration value.
        
        Args:
            sec: Configuration section (or None for top-level)
            key: Configuration key
        
        Returns:
            Configuration value
        """
        if sec:
            return self.cfg.get(sec, {}).get(key)
        return self.cfg.get(key)
    
    def on_save(self) -> None:
        """Save configuration and start application."""
        numeric_keys = {
            ("style", "max_line_length"),
            ("comment", "enabled"), ("comment", "global_cooldown"), ("comment", "per_user_cooldown"),
            ("comment", "min_length"), ("comment", "max_replies_per_min"),
            ("comment", "respond_to_greetings"), ("comment", "greeting_cooldown"),
            ("comment", "respond_to_thanks"),
            (None, "dedupe_ttl"), ("animaze", "port"),
            ("microphone", "enabled"), ("microphone", "attack_ms"), ("microphone", "release_ms"),
            ("microphone", "flush_delay_ms"),
            ("join_rules", "enabled"), ("join_rules", "greet_after_seconds"),
            ("join_rules", "active_ttl_seconds"),
            ("join_rules", "min_idle_since_last_output_sec"),
            ("join_rules", "greet_global_cooldown_sec"),
            ("outbox", "window_seconds"), ("outbox", "max_items"), ("outbox", "max_chars"),
            ("speech", "wait_start_timeout_ms"), ("speech", "max_speech_ms"),
            ("speech", "post_gap_ms")
        }
        float_keys = {("comment", "reply_threshold"), ("microphone", "silence_threshold")}
        list_keys = {("comment", "ignore_if_startswith"), ("comment", "ignore_contains")}
        
        for (sec, key), var in self.vars.items():
            v = var.get().strip()
            if (sec, key) in list_keys:
                items = [x.strip() for x in v.split(",") if x.strip()]
                if sec:
                    self.cfg.setdefault(sec, {})[key] = items
                else:
                    self.cfg[key] = items
                continue
            
            if (sec, key) in float_keys:
                try:
                    v = float(v)
                except ValueError:
                    messagebox.showerror("Ungültiger Wert", f"{key} muss eine Kommazahl sein.")
                    return
            elif (sec, key) in numeric_keys:
                try:
                    v = int(float(v))
                except ValueError:
                    messagebox.showerror("Ungültiger Wert", f"{key} muss eine Zahl sein.")
                    return
            
            if sec:
                self.cfg.setdefault(sec, {})[key] = v
            else:
                self.cfg[key] = v
        
        save_settings(self.cfg)
        messagebox.showinfo("Gespeichert", "Einstellungen gespeichert. Starte…")
        
        # Start application in background thread
        threading.Thread(target=lambda: asyncio.run(self.start_callback(self.cfg, self)), daemon=True).start()
