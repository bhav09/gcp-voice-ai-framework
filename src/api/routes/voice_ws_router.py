import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from src.core.session_manager import VoiceSessionManager

logger = logging.getLogger("VoiceWebSocketRouter")
router = APIRouter(tags=["Voice WebSockets Stream API"])

@router.websocket("/ws/voice")
async def websocket_voice_endpoint(websocket: WebSocket, session_id: str = "default_ws_session"):
    """Full-duplex WebSockets voice streaming bridge connecting clients directly to Gemini Live API via google-genai SDK."""
    await websocket.accept()
    logger.info(f"WebSocket client connected on /ws/voice [Session: {session_id}]")
    
    manager = VoiceSessionManager(session_id=session_id)
    await manager.initialize()
    client = manager.create_client(provider_type="vertex")
    await client.connect()

    try:
        while True:
            # Receive binary PCM audio frame or text frame from WebSocket client
            message = await websocket.receive()
            if "bytes" in message and message["bytes"]:
                pcm_frame = message["bytes"]
                await client.send_audio_chunk(pcm_frame)
                
                # Echo confirmation / audio turn back
                await websocket.send_json({
                    "event": "audio_received",
                    "bytes_len": len(pcm_frame),
                    "session_id": session_id
                })
            elif "text" in message and message["text"]:
                text_payload = message["text"]
                data = json.loads(text_payload)
                if data.get("action") == "interrupt":
                    res = manager.handle_barge_in()
                    await websocket.send_json({"event": "interrupted", "turn_id": res["new_turn_id"]})
                else:
                    await client.send_text_message(data.get("text", ""))
                    await websocket.send_json({"event": "text_sent", "status": "ok"})
    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected [Session: {session_id}]")
    except Exception as e:
        logger.exception(f"Error in WebSocket voice loop: {str(e)}")
    finally:
        await manager.close_session()
