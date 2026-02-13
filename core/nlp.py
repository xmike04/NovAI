import re

class NLPHandler:
    def __init__(self):
        # Filler words to strip
        self.fillers = [
            r"\buh\b", r"\bum\b", r"\bplease\b", r"\bcan you\b", r"\bcould you\b", 
            r"\bi want to\b", r"\bjust\b", r"\bactually\b", r"\breally\b", r"\bquickly\b"
        ]
        
        # Intent Patterns (Regex)
        # (Pattern, Intent, Entity Extraction Logic or Key)
        self.patterns = [
            (r"what time is it|current time|tell me the time", "get_time", {}),
            (r"what is the date|what's the date|current date|today's date", "get_date", {}),
            
            # Weather patterns split to avoid duplicate group name error
            (r"weather in (?P<location>.*)", "get_weather", "location"),
            (r"weather for (?P<location>.*)", "get_weather", "location"),
            (r"weather", "get_weather", "location"),
            
            # YouTube
            (r"play (?P<query>.*) on youtube", "play_youtube", "query"),
            (r"play (?P<query>.*)", "play_youtube", "query"),
            
            # Google
            (r"search for (?P<query>.*) on google", "google_search", "query"),
            (r"search google for (?P<query>.*)", "google_search", "query"),
            (r"search (?P<query>.*)", "google_search", "query"),
            
            (r"hello|hi there|hey jarvis", "greet", {}),
            (r"goodbye|bye|exit|shut down|terminate", "exit", {})
        ]

    def clean_text(self, text):
        """Removes filler words and explicitly normalizes text."""
        cleaned = text.lower()
        for filler in self.fillers:
            cleaned = re.sub(filler, "", cleaned)
        return cleaned.strip()

    def process(self, text):
        """
        Returns (intent, entities, confidence)
        """
        cleaned_text = self.clean_text(text)
        
        for pattern, intent, entity_key in self.patterns:
            match = re.search(pattern, cleaned_text)
            if match:
                entities = {}
                if isinstance(entity_key, str) and entity_key:
                    # Named group extraction if supported or flexible
                    # For basic python re, we use named groups in pattern
                    val = match.group(entity_key) if f"?P<{entity_key}>" in pattern else None
                    if val:
                        entities[entity_key] = val.strip()
                    elif match.groups():
                        # Fallback for simple capture groups
                        entities["query"] = match.group(1).strip()
                
                return intent, entities, 1.0 # High confidence for exact regex match
        
        # No match found
        return "unknown", {}, 0.0
