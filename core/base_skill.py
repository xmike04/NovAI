from typing import List
from NOVA.core.types import SkillResponse

class BaseSkill:
    def __init__(self):
        self.name: str = "BaseSkill"
        self.intents: List[str] = []
        self.description: str = "No description provided."
        self.slots: dict = {} # e.g. {"location": "City name"}
        self.requires_approval: bool = False
    
    def execute(self, entities: dict) -> SkillResponse:
        """
        Execute the skill logic.
        :param entities: Dictionary of extracted entities from NLP.
        :return: SkillResponse object.
        """
        raise NotImplementedError("Skill must implement execute method.")
