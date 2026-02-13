from NOVA.core.base_skill import BaseSkill
from NOVA.core.types import SkillResponse
import pywhatkit

class YoutubeSkill(BaseSkill):
    def __init__(self):
        super().__init__()
        self.name = "YoutubeSkill"
        self.intents = ["play_youtube"]
        self.description = "Play a video on YouTube."
        self.slots = {"query": "Video topic or song name"}

    def execute(self, entities: dict) -> SkillResponse:
        topic = entities.get("query", "")
        if not topic:
             topic = entities.get("row_text", "").replace("play", "").strip()
             
        if topic:
            pywhatkit.playonyt(topic)
            return SkillResponse(text=f"Playing {topic} on YouTube.")
        else:
            return SkillResponse(text="I didn't catch what you wanted to play.", success=False)