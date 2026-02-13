from PyQt5 import QtCore
from NOVA.core.base_skill import BaseSkill
from NOVA.core.types import SkillResponse
import json
import os

class WorkflowSkill(QtCore.QObject, BaseSkill):
    request_workflow_execution = QtCore.pyqtSignal(list) # List of command strings

    def __init__(self):
        QtCore.QObject.__init__(self)
        BaseSkill.__init__(self)
        self.name = "WorkflowSkill"
        self.intents = ["create_workflow", "run_workflow"]
        self.description = "Use this to CREATE a new sequence of actions or RUN an existing automation. Triggers on 'create workflow', 'run workflow', 'start workflow'."
        self.slots = {
            "name": "Name of the workflow",
            "steps": "Steps (comma separated) for creation"
        }
        
        self.workflows_file = os.path.join(os.path.dirname(__file__), "../config/workflows.json")
        self._load_workflows()

    def _load_workflows(self):
        self.workflows = {}
        if os.path.exists(self.workflows_file):
            try:
                with open(self.workflows_file, 'r') as f:
                    self.workflows = json.load(f)
            except:
                pass

    def _save_workflows(self):
         with open(self.workflows_file, 'w') as f:
             json.dump(self.workflows, f, indent=4)

    def execute(self, entities: dict) -> SkillResponse:
        intent = entities.get("intent") # Assuming we can infer or passed explicitly if we modify Manager?
        # Check slots to infer intent if intent name is ambiguous or missing
        # "Create workflow" vs "Run workflow"
        
        # NOTE: SkillManager currently doesn't pass the INTENT name to execute().
        # We rely on "steps" slot being present for creation?
        # Or look at raw text?
        
        raw_text = entities.get("raw_text", "").lower()
        name = entities.get("name", "")
        steps = entities.get("steps", "")
        
        # Heuristic for Creation
        if "create" in raw_text or "make" in raw_text or steps:
             if not name:
                 return SkillResponse(text="What should I call this workflow?", success=False)
             if not steps:
                 return SkillResponse(text="What steps should be in this workflow?", success=False)
                 
             # Parse steps
             # "Open spotify, wait 5 seconds, play music" -> ["Open spotify", "wait 5 seconds", "play music"]
             step_list = [s.strip() for s in steps.replace(" then ", ",").split(",")]
             
             self.workflows[name.lower()] = step_list
             self._save_workflows()
             return SkillResponse(text=f"Created workflow '{name}' with {len(step_list)} steps.")

        # Heuristic for Execution
        if "run" in raw_text or "start" in raw_text or "execute" in raw_text:
             if not name:
                 # Try to extract name from query if slot failed?
                 # "Run morning routine"
                 parts = raw_text.split("run ")
                 if len(parts) > 1:
                     name = parts[1].strip()
             
             name_key = name.lower()
             if name_key in self.workflows:
                 step_list = self.workflows[name_key]
                 self.request_workflow_execution.emit(step_list)
                 return SkillResponse(text=f"Starting workflow '{name}'...")
             else:
                 return SkillResponse(text=f"I couldn't find a workflow named '{name}'.", success=False)

        return SkillResponse(text="I'm not sure if you want to create or run a workflow.", success=False)
