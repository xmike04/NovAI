from NOVA.core.llm import LLMHandler
import random

class MoodDetector:
    def __init__(self):
        self.llm = LLMHandler()

    def analyze(self, text):
        """
        Analyze sentiment of the text.
        Returns: 'positive', 'neutral', 'negative'
        """
        if not text:
            return "neutral"
            
        # 1. Try LLM if available (and fast enough? might be slow for every input)
        # To keep latency low, we might only check for strong words first or use a very fast LLM call.
        # But per requirements: "Implement sentiment analysis ... using OpenAI GPT-3.5-turbo".
        
        try:
            prompt = f"""Classify the sentiment of this text as 'positive', 'neutral', or 'negative'. Return LABEL ONLY.
Text: "{text}"
Label:"""
            # Use low max_tokens to save cost/time
            result = self.llm.generate(prompt, max_tokens=5, stream=False)
            label = result.lower().strip()
            
            if "positive" in label: return "positive"
            if "negative" in label: return "negative"
            return "neutral"
        except:
            # Fallback (Simple Keywords)
            return self._fallback_analyze(text)

    def _fallback_analyze(self, text):
        text = text.lower()
        pos_words = ["happy", "good", "great", "love", "awesome", "excellent", "fun"]
        neg_words = ["sad", "bad", "hate", "terrible", "awful", "angry", "upset"]
        
        if any(w in text for w in pos_words): return "positive"
        if any(w in text for w in neg_words): return "negative"
        return "neutral"
