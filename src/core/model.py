from typing import List, Optional
from pydantic import BaseModel

from core.prj_config import prj_config

class CameraCreateRequest(BaseModel):
    rtsp_link: str
    ai_engine_recognition_url : Optional[str] = None
    realtime: bool = False
    realtime_push_url: Optional[str]
    camera_type: Optional[str]

class AIResponse(BaseModel):
    pass
