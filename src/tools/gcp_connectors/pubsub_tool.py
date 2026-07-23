import os
import json
import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from google.cloud import pubsub_v1
from ..base_tool import BaseVoiceTool

logger = logging.getLogger("PubSubTool")

class PubSubArgs(BaseModel):
    topic_id: str = Field(description="Cloud Pub/Sub topic ID")
    event_data: Dict[str, Any] = Field(description="JSON payload of event to publish")

class PubSubTool(BaseVoiceTool):
    """Google Cloud Pub/Sub event publisher tool for async action orchestration."""

    name = "publish_pubsub_event"
    description = "Publishes asynchronous notification/action events to Google Cloud Pub/Sub topics."
    args_schema = PubSubArgs

    def __init__(self, project_id: Optional[str] = None):
        self.project_id = project_id or os.getenv("GCP_PROJECT_ID", "YOUR_GCP_PROJECT_ID")
        self._publisher = None

    def _get_publisher(self):
        if not self._publisher:
            self._publisher = pubsub_v1.PublisherClient()
        return self._publisher

    async def execute(self, topic_id: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"Publishing Pub/Sub event to topic [{topic_id}] in project [{self.project_id}]")
        try:
            publisher = self._get_publisher()
            topic_path = publisher.topic_path(self.project_id, topic_id)
            data_bytes = json.dumps(event_data).encode("utf-8")
            future = publisher.publish(topic_path, data=data_bytes)
            message_id = future.result()
            return {"status": "published", "message_id": message_id, "topic": topic_id}
        except Exception as e:
            logger.warning(f"PubSub publish notice: {str(e)}")
            return {"status": "mock_published", "topic": topic_id, "notice": str(e)}
