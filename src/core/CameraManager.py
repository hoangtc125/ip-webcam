import requests
import pickle
import threading
from typing import Dict
import uuid
from pydantic import BaseModel
from core.camera.AbstractCamera import BaseCamera
from core.dict import TwoWayDict
import cv2

from core.model import AIResponse
from core.prj_config import prj_config

class PredictPayload(BaseModel):
    cam_id: str
    data: bytes
    img_type: str = "PICKLE"

image_queue = []
def save_image(img, path, size=None):
    print(f'_______ init threading save image ----')
    if size is not None:
        img = cv2.resize(img, size)
    cv2.imwrite(path, img)

def wait_to_save(event: threading.Event):
    global image_queue
    while True:
        try:
            if not image_queue:
                event.clear()
                event.wait()
            save_image(*image_queue.pop())
        except:
            pass

def create_saving_thread(event: threading.Event = threading.Event()):
    worker_thread = threading.Thread(target=wait_to_save, args=(event, ))
    worker_thread.daemon = True
    worker_thread.start()


def ai_process(frame, ai_engine_recognition_url, id):
    pass

def forward_ai_data(data: AIResponse, push_url):
    pass


class CameraManager:
    def __init__(self):
        self.__cameras : Dict[str, BaseCamera] = {}
        self.__streaming_map = TwoWayDict()
        self.event = threading.Event()
        create_saving_thread(self.event)

    def turn_on_realtime(self, rtsp_link):
        self.__cameras[rtsp_link].turn_on_realtime_worker(ai_process, forward_ai_data, time_interval=0.2)
        
    def get_status(self,rtsp_link):
        return rtsp_link in self.__cameras

    def add_camera(self, model: BaseCamera, rtsp_link,  ai_engine_recognition_url, realtime, realtime_push_url, *args, **kwargs):
        if rtsp_link not in self.__cameras:
            self.__cameras[rtsp_link] = model(
            *args, **kwargs,
            rtsp_link=rtsp_link,
            ai_engine_recognition_url= ai_engine_recognition_url,
            realtime_push_url=realtime_push_url) 
            if realtime:
                self.__cameras[rtsp_link].ai_engine_recognition_url=ai_engine_recognition_url
                self.__cameras[rtsp_link].realtime_push_url=realtime_push_url
                self.turn_on_realtime(rtsp_link)
            else:
                self.turn_off_realtime(rtsp_link)
        return "Success"

    def delete_camera(self, rtsp_link):
        self.__cameras[rtsp_link].kill_reader()
        del self.__cameras[rtsp_link]
        del self.__streaming_map[rtsp_link]

    def turn_off_realtime(self, rtsp_link):
        self.__cameras[rtsp_link].turn_off_realtime_worker()

    def get_streaming_iterator(self, rtsp_link):
        return self.__cameras[rtsp_link].get_streaming_iterator()

    def capture(self, rtsp_link, path = None):
        rand = uuid.uuid4()
        if not path:
            path = prj_config.LOG_FOLDER + f"/{rand}.jpg"
        frame = self.__cameras[rtsp_link].get_current_frame()
        yield f"public/{rand}.jpg"
        global image_queue
        image_queue.append([frame, path])
        self.event.set()
