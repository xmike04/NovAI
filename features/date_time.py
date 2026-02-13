from NOVA.core.base_skill import BaseSkill
from NOVA.core.types import SkillResponse
import datetime

class DateTimeSkill(BaseSkill):
    def __init__(self):
        super().__init__()
        self.name = "DateTimeSkill"
        self.intents = ["get_time", "get_date"]

    def execute(self, entities: dict) -> SkillResponse:
        intent = entities.get("intent", "") # Ideally passed explicitly, but we'll assume manager passes it or we handle logic
        # Since BaseSkill execute usually takes entities, we might need 'intent' name passed in.
        # But wait, SkillManager finds the skill BY intent.
        # So we can just check what time/date is requested? 
        # Actually, for multi-intent skills, we might need to know WHICH intent triggered it.
        # Let's assume entities usually doesn't contain intent string in my current NLP.
        # FOR NOW, I will implement generic logic or separate skills.
        # Or better: I'll handle both based on context or just return both?
        # Simpler: let's infer from the passed intent argument in execute? 
        # BaseSkill.execute signature in my plan didn't include intent.
        # I will update BaseSkill to include intent in `execute(self, intent, entities)`. 
        # But I already wrote `base_skill.py`.
        # I'll stick to 1 intent per skill OR just inspect entities if possible.
        # Actually, let's just use datetime.now().
        
        # Hack for now: Logic is simple enough.
        # If the class supports multiple intents, we need to know which one.
        # I will split them into 2 classes in the same file or 1 class handling both?
        # 1 Class handling both is better. 
        # I'll assume I can guess based on entities or just return "Time is X, Date is Y" if unsure, 
        # but actually intent flow separates them.
        
        # Let's update BaseSkill signature in the NEXT step if needed, 
        # but for now I'll just check if the USER said "date" or "time".
        
        # Actually, the SkillManager calls based on intent.
        # I will return a generic response if I can't distinguish, or I'll implement 2 small classes.
        pass

# I will Implement 2 classes for clarity and dynamic loading mapping.
class TimeSkill(BaseSkill):
    def __init__(self):
        super().__init__()
        self.name = "TimeSkill"
        self.intents = ["get_time"]
        self.description = "Gets the current time."
        self.slots = {}
        
    def execute(self, entities: dict) -> SkillResponse:
        now = datetime.datetime.now()
        time_str = now.strftime("%H:%M:%S")
        return SkillResponse(text=f"The current time is {time_str}")

class DateSkill(BaseSkill):
    def __init__(self):
        super().__init__()
        self.name = "DateSkill"
        self.intents = ["get_date"]
        self.description = "Gets the current date."
        self.slots = {}
        
    def execute(self, entities: dict) -> SkillResponse:
        now = datetime.datetime.now()
        date_str = now.strftime("%b %d %Y")
        return SkillResponse(text=f"Today's date is {date_str}")