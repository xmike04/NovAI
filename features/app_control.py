from NOVA.core.base_skill import BaseSkill
from NOVA.core.types import SkillResponse
import subprocess
import os

class AppControlSkill(BaseSkill):
    def __init__(self):
        super().__init__()
        self.name = "AppControlSkill"
        self.intents = ["control_app", "open_app", "close_app"]
        self.description = "Open or Close applications on the computer."
        self.slots = {
            "action": "open or close", 
            "app_name": "Name of the application (e.g. Spotify, Calculator)"
        }
        self.blacklist = ["finder", "dock", "loginwindow", "nova", "python", "terminal", "iterm"]

    def execute(self, entities: dict) -> SkillResponse:
        action = entities.get("action", "open").lower()
        app_name = entities.get("app_name", "")
        
        # Fallback if slots aren't perfectly extracted but we have "open spotify"
        if not app_name and entities.get("query"):
            # Try to parse simple "open X" or "close X" from query
            parts = entities.get("query").split(" ")
            if len(parts) > 1:
                action = parts[0].lower()
                app_name = " ".join(parts[1:])
        
        if not app_name:
             return SkillResponse(text="Which application?", success=False)

        if "open" in action:
            return self._open_app(app_name)
        elif "close" in action or "quit" in action:
            return self._close_app(app_name)
        else:
            return SkillResponse(text=f"I don't know how to '{action}' an app.", success=False)

    def _open_app(self, app_name):
        try:
            # macOS 'open -a "App Name"'
            subprocess.run(["open", "-a", app_name], check=True)
            return SkillResponse(text=f"Opening {app_name}.")
        except Exception as e:
            return SkillResponse(text=f"Failed to open {app_name}. Error: {e}", success=False)

    def _close_app(self, app_name):
        if any(b in app_name.lower() for b in self.blacklist):
            return SkillResponse(text=f"I cannot close {app_name} for safety reasons.", success=False)

        try:
            # macOS AppleScript to quit app gracefully
            script = f'quit app "{app_name}"'
            subprocess.run(["osascript", "-e", script], check=True)
            return SkillResponse(text=f"Closing {app_name}.")
        except Exception as e:
            return SkillResponse(text=f"Failed to close {app_name}. Error: {e}", success=False)
