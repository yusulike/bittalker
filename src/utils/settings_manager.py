"""
Settings Manager Module
Handles persistent storage of user preferences.
"""
import os
import json

DEFAULT_SETTINGS = {
    "interval": 50,
    "voice": "F1",
    "language": "Korean",
    "always_on_top": True,
    "muted": False,
    "ticker_mode": False
}

# Language Code Mapping (shared constant)
LANG_CODE_MAP = {
    "Korean": "ko",
    "English": "en",
    "Spanish": "es",
    "Portuguese": "pt",
    "French": "fr"
}

AVAILABLE_LANGUAGES = list(LANG_CODE_MAP.keys())

class SettingsManager:
    def __init__(self, settings_file="settings.json"):
        # Store in app directory
        self.settings_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            '..', '..', 
            settings_file
        )
        self.settings = self.load()
    
    def load(self):
        """Load settings from JSON file, or return defaults."""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Merge with defaults to handle new keys
                    merged = DEFAULT_SETTINGS.copy()
                    merged.update(loaded)
                    return merged
            except Exception as e:
                print(f"Error loading settings: {e}")
        return DEFAULT_SETTINGS.copy()
    
    def save(self):
        """Save current settings to JSON file."""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def get(self, key, default=None):
        return self.settings.get(key, default)
    
    def set(self, key, value):
        self.settings[key] = value
        self.save()
    
    def update(self, new_settings: dict):
        """Update multiple settings at once and save."""
        self.settings.update(new_settings)
        self.save()
