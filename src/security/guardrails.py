import re
import logging
from typing import Dict, Any, List, Optional
from ..tools.sql_utils import is_mutating_query

logger = logging.getLogger("VoiceGuardrails")

class VoiceGuardrailsEngine:
    """Security, safety, NSFW, and off-topic conversation guardrail enforcement engine."""

    def __init__(self, restricted_keywords: Optional[List[str]] = None):
        self.restricted_keywords = restricted_keywords or ["delete database", "drop table", "shutdown server"]
        
        # Explicit NSFW & Off-Topic detection terms
        self.nsfw_terms = [
            "nsfw", "explicit", "porn", "nude", "sex", "vulgar", "fuck", "shit", "bitch", "asshole", "bastard"
        ]
        
        # Category-based off-topic detection with keyword groups
        self.off_topic_categories = [
            {"keywords": ["joke", "dating", "funny story", "humor"], "category": "entertainment"},
            {"keywords": ["weather", "vacation", "holiday", "travel", "tourism"], "category": "travel"},
            {"keywords": ["football", "soccer", "cricket", "match score", "sports", "basketball", "tennis"], "category": "sports"},
            {"keywords": ["recipe", "cook", "dinner", "food", "restaurant", "cuisine"], "category": "food"},
            {"keywords": ["movie", "film", "netflix", "show recommendation", "tv series", "anime"], "category": "entertainment_media"},
        ]

    def validate_input_transcript(self, text: str) -> Dict[str, Any]:
        """Validate input user transcript for prompt injection, NSFW content, or off-topic conversation."""
        text_lower = text.lower()

        # 1. NSFW Check — use word-boundary regex to avoid false negatives from spacing tricks
        for nsfw in self.nsfw_terms:
            if re.search(r'\b' + re.escape(nsfw) + r'\b', text_lower):
                logger.warning(f"NSFW Guardrail triggered on term: [{nsfw}]")
                return {
                    "is_safe": False,
                    "violation_type": "NSFW_LANGUAGE",
                    "polite_response": "I am designed strictly for professional GCP Voice AI enterprise data analytics and dashboard generation. Please keep our discussion professional and focused on your GCP use case."
                }

        # 2. Off-Topic Check — keyword-category matching instead of hardcoded exact phrases
        for category_group in self.off_topic_categories:
            matched_keywords = [kw for kw in category_group["keywords"] if kw in text_lower]
            if len(matched_keywords) >= 1:
                logger.info(f"Off-Topic Guardrail triggered on category [{category_group['category']}], matched: {matched_keywords}")
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
        # Check SQL/GQL query args for mutations
        sql_arg_names = ["query", "sql_query", "gql_query"]
        for arg_name in sql_arg_names:
            if arg_name in args and isinstance(args[arg_name], str):
                if is_mutating_query(args[arg_name]):
                    return {"allowed": False, "reason": f"Mutating query detected in argument '{arg_name}'"}
        
        # Check for path traversal in collection/document names
        path_args = ["collection", "document_id"]
        for arg_name in path_args:
            if arg_name in args and isinstance(args[arg_name], str):
                if ".." in args[arg_name] or args[arg_name].startswith("/"):
                    return {"allowed": False, "reason": f"Path traversal detected in argument '{arg_name}'"}
        
        return {"allowed": True}
