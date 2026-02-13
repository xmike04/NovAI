import unittest
import sys
import os

# Add the parent directory to sys.path to allow running this script directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from NOVA.core.nlp import NLPHandler
from NOVA.core.skill_manager import SkillManager
# We won't test WakeWord/STT/TTS here as they require hardware/audio

class TestCore(unittest.TestCase):
    def setUp(self):
        self.nlp = NLPHandler()
        self.skill_manager = SkillManager("features")

    def test_nlp_intent(self):
        intent, entities = self.nlp.process("What is the time?")
        self.assertEqual(intent, "get_time")
        
        intent, entities = self.nlp.process("Play Despacito on YouTube")
        self.assertEqual(intent, "play_youtube")
        self.assertEqual(entities["query"], "despacito")

    def test_skill_execution(self):
        # We can't easily test skill execution without mocking dependencies of the skills
        # but we can test the manager's handling of unknown skills
        response = self.skill_manager.execute_skill("unknown_intent", {})
        self.assertIn("not sure", response)

if __name__ == '__main__':
    unittest.main()
