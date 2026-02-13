import json
import os
from NOVA.core.logger import logger

SETTINGS_FILE = "settings.json"

DEFAULT_SETTINGS = {
    "voice_id": "Victoria",
    "voice_speed": 200,
    "wake_word_sensitivity": 0.5,
    "wake_word_model": "Porcupine (Local)"
}

class ConfigManager:
    def __init__(self):
        self.settings = self.load_settings()

    def load_settings(self):
        if not os.path.exists(SETTINGS_FILE):
            logger.info("No settings file found. Creating defaults.")
            self.save_all(DEFAULT_SETTINGS)
            return DEFAULT_SETTINGS.copy()
            
        try:
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
            return DEFAULT_SETTINGS.copy()

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        self.settings[key] = value
        self.save_all(self.settings)

    def save_all(self, settings):
        try:
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(settings, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving settings: {e}")

# Singleton instance
config_manager = ConfigManager()
