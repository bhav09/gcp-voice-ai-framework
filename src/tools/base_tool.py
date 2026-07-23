from abc import ABC, abstractmethod
from typing import Dict, Any, Type
import base64
from pydantic import BaseModel

class BaseVoiceTool(ABC):
    """Abstract base class for all Voice Agent tool integrations."""

    name: str
    description: str
    args_schema: Type[BaseModel]

    def _map_type_to_gemini(self, prop_info: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively maps Pydantic JSON schema types to Gemini OpenAPI types."""
        py_type = prop_info.get("type", "string")
        
        # Unnest anyOf/oneOf optional types if present
        if "anyOf" in prop_info:
            types = [t.get("type") for t in prop_info["anyOf"] if t.get("type") != "null"]
            if types:
                py_type = types[0]

        type_map = {
            "string": "STRING",
            "integer": "INTEGER",
            "number": "NUMBER",
            "boolean": "BOOLEAN",
            "array": "ARRAY",
            "object": "OBJECT"
        }
        
        gemini_type = type_map.get(py_type, "STRING")
        result = {
            "type": gemini_type,
            "description": prop_info.get("description", "")
        }

        if gemini_type == "ARRAY" and "items" in prop_info:
            result["items"] = self._map_type_to_gemini(prop_info["items"])
        elif gemini_type == "OBJECT" and "properties" in prop_info:
            result["properties"] = {
                k: self._map_type_to_gemini(v)
                for k, v in prop_info["properties"].items()
            }
            if "required" in prop_info:
                result["required"] = prop_info["required"]

        return result

    def to_gemini_function_declaration(self) -> Dict[str, Any]:
        """Generate Gemini OpenAPI Function Declaration schema from Pydantic model."""
        schema = self.args_schema.model_json_schema()
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    k: self._map_type_to_gemini(v)
                    for k, v in properties.items()
                },
                "required": required
            }
        }

    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Asynchronously execute tool action and return result dictionary."""
        pass
