import sys
import os
sys.path.append(os.getcwd())

from NOVA.core.skill_manager import SkillManager
from NOVA.core.logger import logger

# Mute logger for test
import logging
logger.setLevel(logging.CRITICAL)

print("--- Testing Skill Loading ---")
sm = SkillManager()
found_ingest = False
found_retrieve = False

for intent, skill in sm.skills.items():
    print(f"Intent: {intent} -> Skill: {skill.name}")
    if skill.name == "KnowledgeIngestionSkill": found_ingest = True
    if skill.name == "KnowledgeRetrievalSkill": found_retrieve = True

if found_ingest and found_retrieve:
    print("SUCCESS: Both Knowledge Skills loaded.")
else:
    print("FAILURE: Knowledge Skills not loaded correctly.")

print("\n--- Testing Routing ---")
text = "What libraries are in the requirements file?"
print(f"Query: '{text}'")

# Simulate main.py routing logic
# We need to see if it picks the right tool via LLM or Intent
response = sm.route_request(text)

print(f"Response Intent: {getattr(response, 'intent', 'None')}")
print(f"Response Text: {response.text[:100]}...") # truncate
