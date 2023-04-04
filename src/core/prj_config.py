import os
import json
from os import getenv
import uuid
from dotenv import load_dotenv
from pydantic import BaseSettings

BASE_DIR = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "../../"))
load_dotenv(os.path.join(BASE_DIR, ".env"))
    
def get_pc_unique_id():
    return str(hex(uuid.getnode()))

class PrjConfig(BaseSettings):
    SERVICE_NAME = getenv("SERVICE_NAME", "CAMERA_SERVICE")
    SECRET_KEY = getenv("SECRET_KEY", "123456")
    CAMERA_SERVICE_PORT = getenv("CAMERA_SERVICE_PORT", "8002")
    SECURITY_ALGORITHM = getenv("SECURITY_ALGORITHM", "HS256")
    LOG_FOLDER = BASE_DIR + r"/public"
    UNIQUE_ID = get_pc_unique_id()
    REALTIME_INTERVAL=getenv("REALTIME_INTERVAL", 0.2)
    NETWORK_CACHING=getenv("NETWORK_CACHING", 100)
    WIDTH_FRAME=getenv("WIDTH_FRAME", 854)
    HEIGHT_FRAME=getenv("HEIGHT_FRAME", 480)

prj_config = PrjConfig()
print("--- Camera Service Config: \n", json.dumps(prj_config.dict(), indent=4))
