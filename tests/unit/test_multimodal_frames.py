import pytest
import base64
from src.core.vertex_client import VertexAILiveClient
from src.core.aistudio_client import AIStudioLiveClient

@pytest.mark.asyncio
async def test_vertex_camera_frame_streaming():
    client = VertexAILiveClient(region="us-central1")
    await client.connect()
    
    # Simulated 1x1 JPEG camera frame
    fake_jpeg = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xff\xdb\x00C\x00\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xbf\x00\xff\xd9"
    await client.send_realtime_media_frame(fake_jpeg, mime_type="image/jpeg")
    assert client.is_connected

@pytest.mark.asyncio
async def test_aistudio_camera_frame_streaming():
    client = AIStudioLiveClient(api_key="TEST_KEY")
    await client.connect()
    
    fake_png = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\rIDATx\x9cc`\x00\x00\x00\x02\x00\x01H\xafA4\x00\x00\x00\x00IEND\xaeB`\x82"
    await client.send_realtime_media_frame(fake_png, mime_type="image/png")
    assert client.is_connected
