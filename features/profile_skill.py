from NOVA.core.base_skill import BaseSkill
from NOVA.core.types import SkillResponse
from NOVA.core.profile import profile_manager

class ProfileSkill(BaseSkill):
    def __init__(self):
        super().__init__()
        self.name = "ProfileSkill"
        self.intents = ["update_profile", "get_profile"]
        self.description = "Save user facts (e.g. 'I like sushi', 'My name is Eric', 'I possess X') OR query stored user info."
        self.slots = {
            "key": "The topic (e.g. name, food, language)", 
            "value": "The fact to save (e.g. 'Sushi', 'Python'). LEAVE EMPTY if querying."
        }

    def execute(self, entities: dict) -> SkillResponse:
        key = entities.get("key", "").lower()
        value = entities.get("value", "")
        raw_text = entities.get("raw_text", "")
        
        # Check if 'value' is actually a question (Router error)
        question_starters = ["what", "who", "where", "when", "why", "how", "does", "do ", "is "]
        if value and any(value.lower().startswith(q) for q in question_starters):
            # Treat as query
            if not key:
                # Try to extract key from value? e.g. "What language..." -> "language"
                # Simple fallback: use the value as the raw query text
                pass
            value = "" # Clear value so it hits Query logic
        
        # 1. Update Name
        if "name" in key and value:
             profile_manager.set("name", value)
             return SkillResponse(text=f"Okay, I'll call you {value} from now on.")

        # 2. Update Fact/Preference
        if value:
            profile_manager.add_fact(value)
            return SkillResponse(text=f"I've noted that: {value}")

        # 3. Query Name
        if "name" in key or "who am i" in raw_text.lower():
            name = profile_manager.get("name", "User")
            return SkillResponse(text=f"Your name is {name}.")

        # 4. Query Facts (General)
        # If we just get "get_profile" with no slots, maybe show everything?
        if not value:
            name = profile_manager.get("name", "User")
            facts = profile_manager.get("facts", [])
            if facts:
                fact_str = ". ".join(facts)
                return SkillResponse(text=f"You are {name}. I also know: {fact_str}")
            return SkillResponse(text=f"You are {name}.")

        return SkillResponse(text="I wasn't sure if you wanted to update or query your profile.", success=False)
