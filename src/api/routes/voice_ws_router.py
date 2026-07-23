import json
import base64
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from src.core.session_manager import VoiceSessionManager

logger = logging.getLogger("VoiceWebSocketRouter")
router = APIRouter(tags=["Voice WebSockets Stream API"])

@router.websocket("/ws/voice")
async def websocket_voice_endpoint(websocket: WebSocket, session_id: str = "default_ws_session"):
    """Full-duplex WebSockets voice & multimodal media streaming bridge connecting clients directly to Gemini Live API via google-genai SDK."""
    await websocket.accept()
    logger.info(f"WebSocket client connected on /ws/voice [Session: {session_id}]")
    
    manager = VoiceSessionManager(session_id=session_id)
    await manager.initialize()
    client = manager.create_client(provider_type="vertex")
    await client.connect()

    try:
        while True:
            # Receive binary PCM audio frame, binary camera image frame, or JSON text control payload
            message = await websocket.receive()
            if "bytes" in message and message["bytes"]:
                raw_bytes = message["bytes"]
                # Detect JPEG (0xFFD8) or PNG (0x8950) magic bytes for camera video frames vs raw audio PCM
                if raw_bytes.startswith(b"\xff\xd8") or raw_bytes.startswith(b"\x89PNG"):
                    mime = "image/jpeg" if raw_bytes.startswith(b"\xff\xd8") else "image/png"
                    await client.send_realtime_media_frame(raw_bytes, mime_type=mime)
                    await websocket.send_json({"event": "media_frame_received", "mime": mime, "bytes_len": len(raw_bytes)})
                else:
                    await client.send_audio_chunk(raw_bytes)
                    await websocket.send_json({"event": "audio_received", "bytes_len": len(raw_bytes), "session_id": session_id})

            elif "text" in message and message["text"]:
                text_payload = message["text"]
                data = json.loads(text_payload)
                
                if data.get("action") == "interrupt":
                    res = manager.handle_barge_in()
                    await websocket.send_json({"event": "interrupted", "turn_id": res["new_turn_id"]})
                elif data.get("action") == "image_frame" or "image_base64" in data:
                    img_data = base64.b64decode(data.get("image_base64", ""))
                    mime = data.get("mime_type", "image/jpeg")
                    await client.send_realtime_media_frame(img_data, mime_type=mime)
                    await websocket.send_json({"event": "media_frame_received", "mime": mime, "status": "ok"})
                else:
                    await client.send_text_message(data.get("text", ""))
                    await websocket.send_json({"event": "text_sent", "status": "ok"})

    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected [Session: {session_id}]")
    except Exception as e:
        logger.exception(f"Error in WebSocket voice loop: {str(e)}")
    finally:
        await manager.close_session()
