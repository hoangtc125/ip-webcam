import traceback
from threading import Lock
import threading
import numpy as np
import cv2
import time
import vlc
from PIL import Image
import ctypes

from src.core.camera.AbstractCamera import BaseCamera
from src.core.prj_config import prj_config


class VLC_Camera(BaseCamera):
	last_frame = None
	last_ready = None
	lock = Lock()
	vlcInstance = vlc.Instance(f'--network-caching={prj_config.NETWORK_CACHING}')

	def __init__(
		self,
		rtsp_link,
		ai_engine_recognition_url,
		realtime_push_url,
		camera_type,
		stop=threading.Event(),
		framerate = 24):
		"""
		Initialize the stream capturing process
		link - rstp link of stream
		stop - to send commands to this process
		outPipe - this process can send commands outside
		"""
		super().__init__(rtsp_link,ai_engine_recognition_url, realtime_push_url)
		self.stop = stop
		self.last_frame = None
		self.framerate = framerate
		self.sink = None
		self.image_arr = None
		self.newImage = False
		self.width_frame_return = int(prj_config.WIDTH_FRAME)
		self.height_frame_return = int(prj_config.HEIGHT_FRAME)
		self.camera_type = camera_type

		self.thread = threading.Thread(target=self.rtsp_cam_buffer)
		self.thread.daemon = True
		self.thread.start()

		self.thread = threading.Thread(target=self.decode_image_worker)
		self.thread.daemon = True
		self.thread.start()

	def decode_image_worker(self):
		while True:
			try:
				self.stop.clear()
				self.stop.wait()
				img = Image.frombuffer(
					"RGBA", (self.width_frame_return, self.height_frame_return), self.newImage, "raw", "BGRA", 0, 1)
				self.image_arr =  cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
				
			except:
				traceback.print_exc()
				pass
		
	def rtsp_cam_buffer(self):
		
		pl = self.vlcInstance.media_player_new()
		pl.set_mrl(self.rtsp_link)
		pl.audio_set_volume(100)

		VIDEOWIDTH = self.width_frame_return
		VIDEOHEIGHT = self.height_frame_return
		# size in bytes when RV32
		size = VIDEOWIDTH * VIDEOHEIGHT * 4
		# allocate buffer
		buf = (ctypes.c_ubyte * size)()
		# get pointer to buffer
		buf_p = ctypes.cast(buf, ctypes.c_void_p)

		CorrectVideoLockCb = ctypes.CFUNCTYPE(
			ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p))

		@CorrectVideoLockCb
		def _lockcb(opaque, planes):
			planes[0] = buf_p

		@vlc.CallbackDecorators.VideoDisplayCb
		def set_current_buffer(opaque, picture):
			self.newImage=buf
			self.stop.set()

		def audio_callback(data, format, nb_samples, pts):
			# write audio to file
			print(data)

		vlc.libvlc_video_set_callbacks(pl, _lockcb, None, set_current_buffer, None)
		vlc.libvlc_audio_set_callbacks(pl, audio_callback, None, None, None)

		pl.video_set_format("RV32", VIDEOWIDTH, VIDEOHEIGHT, VIDEOWIDTH * 4)
		pl.play()
		time.sleep(100)
		while True:
			if vlc.State.Ended == pl.get_state():
				pl.set_mrl(self.rtsp_link)
				vlc.libvlc_video_set_callbacks(
					pl, _lockcb, None, set_current_buffer, None)
				pl.video_set_format("RV32", VIDEOWIDTH,
									VIDEOHEIGHT, VIDEOWIDTH * 4)
				pl.play()
			time.sleep(5)

	def get_current_frame(self):
		return self.image_arr

	def get_streaming_iterator(self):
		header = "--jpgboundary\r\nContent-Type: image/jpeg\r\n"
		prefix = ""
		while True:
			start = time.time()
			frame = self.get_current_frame()
			_, jpeg = cv2.imencode(
				".jpg",
				frame,
				params=(cv2.IMWRITE_JPEG_QUALITY, 70),
			)
			msg = (
				prefix
				+ header
				+ "Content-Length: {}\r\n\r\n".format(len(jpeg.tobytes()))
			)

			yield (msg.encode("utf-8") + jpeg.tobytes())
			prefix = "\r\n"
			exec_time = time.time() - start
			time.sleep(max(1 / self.framerate - exec_time, 0))

if __name__ == "__main__":

	from fastapi import FastAPI
	from fastapi.middleware.cors import CORSMiddleware
	from fastapi.responses import StreamingResponse

	app = FastAPI(docs_url=None, redoc_url=None)
	app.add_middleware(
		CORSMiddleware,
		allow_origins=['*'],
		allow_credentials=True,
		allow_methods=["*"],
		allow_headers=["*"],
	)

	vlc_cam = VLC_Camera("http://192.168.1.222:8080/video", None, None, None)

	@app.get("/stream/video")
	def streaming_video():
		return StreamingResponse(
			vlc_cam.get_streaming_iterator(),
			media_type="multipart/x-mixed-replace; boundary=jpgboundary"
		)
	
	@app.get("/stream/audio")
	def streaming_audio():
		pass
	
	
	import uvicorn
	uvicorn.run(app, host="0.0.0.0", port=int(8001))
