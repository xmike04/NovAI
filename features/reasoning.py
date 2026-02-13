from PyQt5 import QtCore
from NOVA.core.base_skill import BaseSkill
from NOVA.core.types import SkillResponse
from NOVA.core.llm import LLMHandler
import json

class ReasoningSkill(QtCore.QObject, BaseSkill):
    request_sequence = QtCore.pyqtSignal(list) # Re-using the concept of sequence execution

    def __init__(self):
        QtCore.QObject.__init__(self)
        BaseSkill.__init__(self)
        self.name = "ReasoningSkill"
        self.intents = ["decompose_task", "solve_complex"]
        self.description = "Break down complex requests into multiple steps."
        self.slots = {
            "task": "The complex task description"
        }
        self.llm = LLMHandler()

    def execute(self, entities: dict) -> SkillResponse:
        task = entities.get("task") or entities.get("raw_text")
        if not task:
            return SkillResponse(text="What complex task should I solve?", success=False)

        # Prompt LLM to decompose
        # We need it to output a JSON list of strings that NOVA can understand.
        prompt = f"""You are NOVA's planning engine.
User Request: "{task}"

Break this down into a sequential list of simple voice commands that NOVA can understand.
NOVA understands: "Open [App]", "Close [App]", "Set alarm for [Time]", "Search google for [Query]", "What is the weather", "Play [Topic] on youtube".

Output JSON ONLY:
["command 1", "command 2", ...]
"""
        try:
            llm_output = self.llm.generate(prompt, model="gpt-3.5-turbo")
            # Cleaning
            if "```json" in llm_output:
                llm_output = llm_output.split("```json")[1].split("```")[0].strip()
            elif "```" in llm_output:
                llm_output = llm_output.split("```")[1].split("```")[0].strip()
            
            steps = json.loads(llm_output)
            
            if isinstance(steps, list) and len(steps) > 0:
                self.request_sequence.emit(steps)
                return SkillResponse(text=f"I've broken that down into {len(steps)} steps. Executing now.")
            else:
                 return SkillResponse(text="I couldn't verify the plan steps.", success=False)

        except Exception as e:
            return SkillResponse(text=f"Planning failed: {e}", success=False)
