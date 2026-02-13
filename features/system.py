from PyQt5 import QtCore
from NOVA.core.base_skill import BaseSkill
from NOVA.core.types import SkillResponse
from NOVA.core.logger import logger
import logging

class SystemSkill(QtCore.QObject, BaseSkill):
    request_reload = QtCore.pyqtSignal()
    request_log_level = QtCore.pyqtSignal(str)

    def __init__(self):
        QtCore.QObject.__init__(self)
        BaseSkill.__init__(self)
        self.name = "SystemSkill"
        self.intents = ["reload_skills", "set_log_level"]
        self.description = "System management: Reload skills, Configure logging."
        self.slots = {
            "level": "Log level (DEBUG, INFO, WARNING, ERROR)"
        }

    def execute(self, entities: dict) -> SkillResponse:
        intent = entities.get("intent") # Main might not pass intent directly in entities if regex?
        # But we can infer from slot presence or check if we store current intent somewhere?
        # SkillManager.execute_skill passes entities.
        # But wait, execute_skill calls self.skills[intent].execute(entities).
        # But execute doesn't receive the intent name.
        # So I have to guess base on slots or entities.
        
        # Or I can look at the raw command?
        # "Reload skills" -> No slots.
        # "Set log level to DEBUG" -> Level slot.
        
        level = entities.get("level")
        if level: 
            # Likely set_log_level
            level_upper = level.upper()
            if level_upper in ["DEBUG", "INFO", "WARNING", "ERROR"]:
                 self.request_log_level.emit(level_upper)
                 return SkillResponse(text=f"Setting log level to {level_upper}.")
            else:
                 return SkillResponse(text=f"Invalid log level: {level}. Use DEBUG, INFO, WARNING, or ERROR.", success=False)
        
        # If no level, and we are here, likely reload (or just bad parsing)
        # Check raw text or just default to reload if "reload" in text?
        # entities might have "raw_text".
        raw_text = entities.get("raw_text", "").lower()
        if "reload" in raw_text or "refresh" in raw_text:
            self.request_reload.emit()
            return SkillResponse(text="Reloading skills...")
            
        return SkillResponse(text="System command recognized but arguments unclear.", success=False)
