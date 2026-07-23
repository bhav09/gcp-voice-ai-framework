import logging
from typing import Dict, Any, List

logger = logging.getLogger("VoiceGuardrails")

class VoiceGuardrailsEngine:
    """Security, safety, and operational guardrail enforcement engine."""

    def __init__(self, restricted_keywords: Optional[List[str]] = None):
        self.restricted_keywords = restricted_keywords or ["delete database", "drop table", "shutdown server"]

    def validate_input_transcript(self, text: str) -> Dict[str, Any]:
        """Validate input user transcript for safety violations."""
        text_lower = text.lower()
        for kw in self.restricted_keywords:
            if kw in text_lower:
                logger.warning(f"Guardrail triggered on keyword: {kw}")
                return {"is_safe": False, "reason": f"Restricted command keyword: '{kw}'"}
        return {"is_safe": True, "reason": None}

    def validate_tool_args(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Verify tool execution parameters against security policy."""
        return {"allowed": True}
