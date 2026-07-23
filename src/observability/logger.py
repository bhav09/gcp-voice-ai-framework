import re
import json
import logging
from typing import Dict, Any

logger = logging.getLogger("StructuredVoiceLogger")

class StructuredVoiceLogger:
    """Structured JSON Logger with Cloud Data Loss Prevention (DLP API) PII masking capability."""

    def __init__(self, enable_dlp_pii_redaction: bool = False):
        self.enable_dlp_pii_redaction = enable_dlp_pii_redaction
        # RegEx patterns for local client-side PII sanitization fallback
        self._pii_patterns = {
            "SSN": r"\b\d{3}-\d{2}-\d{4}\b",
            "CREDIT_CARD": r"\b(?:\d[ -]*?){13,16}\b",
            "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        }

    def sanitize_text(self, text: str) -> str:
        """Mask PII entities in transcript strings prior to logging."""
        if not self.enable_dlp_pii_redaction or not text:
            return text

        sanitized = text
        for pii_type, pattern in self._pii_patterns.items():
            sanitized = re.sub(pattern, f"[{pii_type}_REDACTED]", sanitized)
        return sanitized

    def log_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        """Emit structured JSON log event to Cloud Logging."""
        sanitized_payload = {}
        for k, v in payload.items():
            if isinstance(v, str):
                sanitized_payload[k] = self.sanitize_text(v)
            else:
                sanitized_payload[k] = v

        log_record = {
            "event_type": event_type,
            "payload": sanitized_payload
        }
        logger.info(json.dumps(log_record))
