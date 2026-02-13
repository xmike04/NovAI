import unittest
from unittest.mock import patch, MagicMock
import requests
from NOVA.core.llm import LLMHandler

class TestLLMHandler(unittest.TestCase):
    @patch('core.llm.openai')
    @patch('core.llm.requests')
    def test_online_openai(self, mock_requests, mock_openai):
        # Setup: Online + Key present
        mock_requests.get.return_value.status_code = 200 # Google ping OK
        
        # Ensure we don't accidentally swallow exception type checks if code uses them
        # But here we just mock the .get call success
        
        # Mock OpenAI response
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock(message=MagicMock(content="Hello from OpenAI"))]
        mock_openai.OpenAI.return_value.chat.completions.create.return_value = mock_completion
        
        handler = LLMHandler()
        handler.openai_key = "fake-key"
        
        response = handler.generate("Hi")
        self.assertEqual(response, "Hello from OpenAI")
        
    def test_offline_fallback(self):
        # We need to patch requests.get specifically to modify behavior, 
        # but NOT patch the entire module so we can use requests.ConnectionError
        
        with patch('core.llm.requests.get') as mock_get, \
             patch('core.llm.requests.post') as mock_post:
            
            # Setup: Offline (requests.get fails with ACTUAL requests.ConnectionError)
            def side_effect(*args, **kwargs):
                if "google" in args[0]:
                    raise requests.ConnectionError("Offline")
                return MagicMock()
            
            mock_get.side_effect = side_effect
            
            # Mock local LLM response
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {"response": "Hello from Local"}
            
            handler = LLMHandler()
            # Ensure key is missing to force offline check or fallback logic
            handler.openai_key = None 
            
            response = handler.generate("Hi")
            self.assertEqual(response, "Hello from Local")

if __name__ == '__main__':
    unittest.main()
