from dataclasses import dataclass, field
from typing import Optional, Dict, Any

@dataclass
class SkillResponse:
    text: str 
    intent: str = "unknown" # Added for control flow (e.g. exit)
    success: bool = True
    data: Dict[str, Any] = field(default_factory=dict)
    visual: Optional[str] = None # For future GUI updates (e.g. image path or HTML)
    is_streaming: bool = False
    iterator: Any = None
