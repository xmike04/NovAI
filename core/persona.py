from NOVA.core.config_manager import config_manager
from NOVA.core.profile import profile_manager

DEFAULT_SYSTEM_PROMPT = """You are NOVA (Neural Omni-Voice Assistant), a sophisticated, witty, and helpful AI.
You are concise, professional, but have a touch of dry humor.
You respond in a way that is optimized for Voice Output (TTS):
- Avoid markdown like bold/italic.
- Use natural punctuation.
- Keep responses short (under 2 sentences) unless asked for detail.
"""

class PersonaManager:
    def __init__(self):
        # Load from config or set default
        self.system_prompt = config_manager.get("system_prompt", DEFAULT_SYSTEM_PROMPT)

    def get_prompt(self):
        # Dynamically inject profile context
        context = profile_manager.get_context_string()
        return f"{self.system_prompt}\n\n{context}"

    def set_prompt(self, new_prompt):
        self.system_prompt = new_prompt
        config_manager.set("system_prompt", new_prompt)

    def reset_to_default(self):
        self.set_prompt(DEFAULT_SYSTEM_PROMPT)

persona_manager = PersonaManager()
