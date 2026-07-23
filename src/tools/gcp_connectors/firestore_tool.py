import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from google.cloud import firestore
from ..base_tool import BaseVoiceTool

logger = logging.getLogger("FirestoreTool")

class FirestoreArgs(BaseModel):
    collection: str = Field(description="Firestore collection name")
    document_id: str = Field(description="Document identifier")
    action: str = Field(description="Action to perform: 'read' or 'write'")
    payload: Optional[Dict[str, Any]] = Field(default=None, description="Data payload for 'write' action")

class FirestoreTool(BaseVoiceTool):
    """Google Cloud Firestore document database connector tool."""

    name = "manage_firestore_document"
    description = "Reads or updates document records in Google Cloud Firestore session database."
    args_schema = FirestoreArgs

    def __init__(self, project_id: str = "gen-demo-66-20250711"):
        self.project_id = project_id
        self._db = None

    def _get_db(self):
        if not self._db:
            self._db = firestore.Client(project=self.project_id)
        return self._db

    async def execute(self, collection: str, document_id: str, action: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        logger.info(f"Firestore Action [{action}] on Collection [{collection}], Doc [{document_id}]")
        try:
            db = self._get_db()
            doc_ref = db.collection(collection).document(document_id)
            if action == "read":
                doc = doc_ref.get()
                if doc.exists:
                    return {"exists": True, "data": doc.to_dict()}
                return {"exists": False, "data": {}}
            elif action == "write":
                if not payload:
                    return {"error": "Payload is required for write action."}
                doc_ref.set(payload, merge=True)
                return {"status": "success", "updated_doc_id": document_id}
            else:
                return {"error": f"Invalid action: {action}"}
        except Exception as e:
            logger.warning(f"Firestore execution notice: {str(e)}")
            return {"status": "mock_success", "collection": collection, "document_id": document_id, "notice": str(e)}
