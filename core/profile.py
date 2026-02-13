import json
import os
from NOVA.core.logger import logger

class ProfileManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ProfileManager, cls).__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        self.profile_path = os.path.join(os.path.dirname(__file__), "../config/user_profile.json")
        self.data = {
            "name": "User",
            "preferences": {},
            "facts": []
        }
        self.load()

    def load(self):
        if os.path.exists(self.profile_path):
            try:
                with open(self.profile_path, 'r') as f:
                    data = json.load(f)
                    self.data.update(data)
            except Exception as e:
                logger.error(f"Failed to load user profile: {e}")

    def save(self):
        try:
            os.makedirs(os.path.dirname(self.profile_path), exist_ok=True)
            with open(self.profile_path, 'w') as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save user profile: {e}")

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self.save()

    def update_preference(self, key, value):
        self.data["preferences"][key] = value
        self.save()

    def add_fact(self, fact):
        if fact not in self.data["facts"]:
            self.data["facts"].append(fact)
            self.save()

    def get_context_string(self):
        """Returns a string summary of the user for LLM context."""
        context = f"User Name: {self.data.get('name')}\n"
        
        prefs = self.data.get("preferences", {})
        if prefs:
            context += "Preferences:\n"
            for k, v in prefs.items():
                context += f"- {k}: {v}\n"
        
        facts = self.data.get("facts", [])
        if facts:
            context += "Facts about user:\n"
            for fact in facts:
                context += f"- {fact}\n"
                
        return context

# Singleton instance
profile_manager = ProfileManager()
