import asyncio
import logging
from typing import Dict, Any, List, Optional
from .base_tool import BaseVoiceTool

logger = logging.getLogger("ToolDispatcher")

class ToolDispatcher:
    """Async tool execution dispatcher for Gemini Live function calls."""

    def __init__(self):
        self._tools: Dict[str, BaseVoiceTool] = {}

    def register_tool(self, tool: BaseVoiceTool) -> None:
        """Register a tool instance."""
        self._tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")

    def get_tool_declarations(self) -> List[Dict[str, Any]]:
        """Return list of Gemini function declarations for all registered tools."""
        return [tool.to_gemini_function_declaration() for tool in self._tools.values()]

    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Asynchronously execute registered tool without blocking the audio stream looper."""
        if tool_name not in self._tools:
            logger.error(f"Tool '{tool_name}' not found in registry.")
            return {"error": f"Tool '{tool_name}' is not registered."}

        tool = self._tools[tool_name]
        logger.info(f"Executing tool '{tool_name}' with args: {arguments}")
        try:
            # Execute in non-blocking async context
            result = await tool.execute(**arguments)
            return {"status": "success", "result": result}
        except Exception as e:
            logger.exception(f"Error executing tool '{tool_name}': {str(e)}")
            return {"status": "error", "message": str(e)}
