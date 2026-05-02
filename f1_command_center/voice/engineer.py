"""
Voice engineer — text-to-speech radio commentary with F1 engineer style.

Supported accents: uk, us, india, aussie
Requires: pyttsx3 (offline TTS, no API key needed)

TODO (you): Swap pyttsx3 for ElevenLabs or Google Cloud TTS for
           much higher quality voice output. See README.md.
"""

from __future__ import annotations
import threading
import time

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False


# Voice property presets per accent
# voice_id index is system-dependent — these are sensible defaults
ACCENT_CONFIG = {
    "uk": {
        "rate": 165,
        "pitch": 95,
        "voice_preference": ["english_rp", "english-gb", "en_GB", "en-GB"],
    },
    "us": {
        "rate": 175,
        "pitch": 100,
        "voice_preference": ["english-us", "en_US", "en-US", "english"],
    },
    "india": {
        "rate": 155,
        "pitch": 105,
        "voice_preference": ["english-in", "en_IN", "hindi"],
    },
    "aussie": {
        "rate": 170,
        "pitch": 95,
        "voice_preference": ["english-au", "en_AU", "english"],
    },
}


class VoiceEngineer:
    """
    Thread-safe text-to-speech wrapper.
    Falls back to print() if pyttsx3 is not installed.
    """

    def __init__(self, accent: str = "uk", volume: float = 0.8):
        self.accent  = accent
        self.volume  = max(0.0, min(1.0, volume))
        self._lock   = threading.Lock()
        self._engine = None

        if TTS_AVAILABLE:
            try:
                self._engine = pyttsx3.init()
                self._configure()
            except Exception as e:
                print(f"[VoiceEngineer] TTS init failed: {e} — falling back to print")
                self._engine = None

    def _configure(self):
        if not self._engine:
            return
        cfg = ACCENT_CONFIG.get(self.accent, ACCENT_CONFIG["uk"])
        self._engine.setProperty("rate",   cfg["rate"])
        self._engine.setProperty("volume", self.volume)

        # Try to match the preferred voice for the accent
        voices = self._engine.getProperty("voices")
        for pref in cfg["voice_preference"]:
            for v in voices:
                if pref.lower() in v.id.lower() or pref.lower() in (v.name or "").lower():
                    self._engine.setProperty("voice", v.id)
                    return

    def speak(self, text: str):
        """Speak text. Thread-safe — blocks until speech completes."""
        if not text:
            return
        with self._lock:
            if self._engine:
                try:
                    self._engine.say(text)
                    self._engine.runAndWait()
                except Exception as e:
                    print(f"[VoiceEngineer] speak error: {e}")
                    print(f"[RADIO] {text}")
            else:
                # Graceful fallback
                print(f"[RADIO — {self.accent.upper()}] {text}")
