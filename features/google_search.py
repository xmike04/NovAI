from NOVA.core.base_skill import BaseSkill
from NOVA.core.types import SkillResponse
import webbrowser

class GoogleSkill(BaseSkill):
    def __init__(self):
        super().__init__()
        self.name = "GoogleSkill"
        self.intents = ["google_search"]
        self.description = "Search Google for external information, news, or general knowledge. Do NOT use for saving user facts."
        self.slots = {"query": "What to search for"}

    def execute(self, entities: dict) -> SkillResponse:
        query = entities.get("query", "")
        if query:
            url = f"https://www.google.com/search?q={query}"
            webbrowser.open(url)
            return SkillResponse(text=f"Opened Google Search for {query}.")
        else:
            return SkillResponse(text="What should I search for?", success=False)
