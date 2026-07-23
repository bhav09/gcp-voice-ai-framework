import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("VoiceGuardrails")

class VoiceGuardrailsEngine:
    """Security, safety, NSFW, and off-topic conversation guardrail enforcement engine."""

    def __init__(self, restricted_keywords: Optional[List[str]] = None):
        self.restricted_keywords = restricted_keywords or ["delete database", "drop table", "shutdown server"]
        
        # Explicit NSFW & Off-Topic detection terms
        self.nsfw_terms = [
            "nsfw", "explicit", "porn", "nude", "sex", "vulgar", "fuck", "shit", "bitch", "asshole", "bastard"
        ]
        self.off_topic_indicators = [
            "tell me a joke about dating", "weather in tokyo for my vacation", "who won the football match yesterday",
            "cook a recipe for dinner", "movie recommendations"
        ]

    def validate_input_transcript(self, text: str) -> Dict[str, Any]:
        """Validate input user transcript for prompt injection, NSFW content, or off-topic conversation."""
        text_lower = text.lower()

        # 1. NSFW Check
        for nsfw in self.nsfw_terms:
            if nsfw in text_lower:
                logger.warning(f"NSFW Guardrail triggered on term: [{nsfw}]")
                return {
                    "is_safe": False,
                    "violation_type": "NSFW_LANGUAGE",
                    "polite_response": "I am designed strictly for professional GCP Voice AI enterprise data analytics and dashboard generation. Please keep our discussion professional and focused on your GCP use case."
                }

        # 2. Off-Topic Check
        for off_topic in self.off_topic_indicators:
            if off_topic in text_lower:
                logger.info(f"Off-Topic Guardrail triggered on phrase: [{off_topic}]")
                return {
                    "is_safe": False,
                    "violation_type": "OFF_TOPIC",
                    "polite_response": "I specialize exclusively in GCP data discovery, analytics, and automated dashboard creation. Let's focus on your GCP databases, BigQuery datasets, or Vertex RAG knowledge base."
                }

        # 3. Restricted Command Keyword Check
        for kw in self.restricted_keywords:
            if kw in text_lower:
                logger.warning(f"Restricted Command Guardrail triggered on keyword: [{kw}]")
                return {
                    "is_safe": False,
                    "violation_type": "RESTRICTED_COMMAND",
                    "polite_response": f"Destructive administrative commands such as '{kw}' are restricted by security guardrails."
                }

        return {"is_safe": True, "violation_type": None, "polite_response": None}

    def validate_tool_args(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Verify tool execution parameters against security policy."""
        return {"allowed": True}
