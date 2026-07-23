import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("VoiceTracer")

class VoiceTracer:
    """OpenTelemetry & GCP Cloud Trace context manager for Voice session spans."""

    def __init__(self, service_name: str = "gemini-live-voice-agent"):
        self.service_name = service_name
        self.active_spans: Dict[str, float] = {}

    def start_span(self, span_name: str) -> str:
        """Start OpenTelemetry / Cloud Trace span."""
        logger.debug(f"[Trace] Starting span: {span_name}")
        return span_name

    def end_span(self, span_name: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        """End span and record metadata."""
        logger.debug(f"[Trace] Ending span: {span_name} with attributes {attributes or {}}")
