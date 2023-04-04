from abc import ABC
import asyncio
# from symbol import func_type
import threading
import time


class BaseCamera(ABC):

    def __init__(self, rtsp_link, ai_engine_recognition_url, realtime_push_url, **args) -> None:
        super().__init__()
        self.rtsp_link=rtsp_link
        self.is_running = True
        self.ai_engine_recognition_url = ai_engine_recognition_url
        self.realtime_push_url = realtime_push_url
        self.thread: threading.Thread = None
        self.realtime = False

    def kill_reader(self):
        pass
    
    def get_current_frame(self):
        pass
    
    def get_streaming_iterator(self):
        pass

    def __activate_realtime_ai_worker(self, action = None, time_interval = None, call_back = None):
        if not self.realtime or not action or not time_interval or not call_back:
            raise Exception("realtime mode is off")
        while self.realtime:
            call_back(action(self.get_current_frame(), self.ai_engine_recognition_url, self.rtsp_link), self.realtime_push_url)
            time.sleep(time_interval)

    def turn_on_realtime_worker(self, action, call_back, time_interval=0.05):
        self.realtime=True
        worker_thread = threading.Thread(target=self.__activate_realtime_ai_worker, args=(action, time_interval, call_back, ))
        worker_thread.daemon = True
        worker_thread.start()

    def turn_off_realtime_worker(self):
        self.realtime = False
