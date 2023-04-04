from typing import Union
import uvicorn
import time
from fastapi import FastAPI, Header, Request

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

from core.CameraManager import CameraManager
from core.camera.vlc_camera import VLC_Camera

from core.prj_config import prj_config, BASE_DIR
from core.model import CameraCreateRequest

app = FastAPI(version=1.0, docs_url=None, redoc_url=None)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory=BASE_DIR + r"/static"), name="static")

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )
    
@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()

@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url="/static/redoc.standalone.js",
    )

from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )
    
@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()

@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url="/static/redoc.standalone.js",
    )

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

app.mount('/public', StaticFiles(directory=prj_config.LOG_FOLDER), name="public")

camera_manager = CameraManager()

@app.post("/camera/add")
def add_camera(camera_create_request: CameraCreateRequest):
    global camera_manager
    return camera_manager.add_camera(
        VLC_Camera,
        rtsp_link=camera_create_request.rtsp_link,
        ai_engine_recognition_url=camera_create_request.ai_engine_recognition_url,
        realtime=camera_create_request.realtime,
        realtime_push_url=camera_create_request.realtime_push_url,
        camera_type=camera_create_request.camera_type,
        )

@app.post("/camera/delete")
def add_camera(rtsp_link: str, internal_auth: Union[str, None] = Header(default=None)):
    global camera_manager
    camera_manager.delete_camera(rtsp_link)
    return True

@app.get("/stream")
def streaming(rtsp_link, internal_auth: Union[str, None] = Header(default=None)):
    return StreamingResponse(
        camera_manager.get_streaming_iterator(
            rtsp_link
        ),
        media_type="multipart/x-mixed-replace; boundary=jpgboundary"
    )

@app.post("/camera/capture")
async def capture(rtsp_link: str, internal_auth: Union[str, None] = Header(default=None)):
    global camera_manager
    a = camera_manager.capture(rtsp_link)
    return a

@app.post("/realtime/turn-on")
async def turn_on(rtsp_link: str, internal_auth: Union[str, None] = Header(default=None)):
    global camera_manager
    return camera_manager.turn_on_realtime(rtsp_link)

@app.post("/realtime/turn-off")
async def turn_off(rtsp_link: str, internal_auth: Union[str, None] = Header(default=None)):
    global camera_manager
    return camera_manager.turn_off_realtime(rtsp_link)

uvicorn.run(app, host="0.0.0.0", port=int(prj_config.CAMERA_SERVICE_PORT))
