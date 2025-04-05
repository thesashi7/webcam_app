from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from starlette.websockets import WebSocketDisconnect, WebSocketState
from webcam import Webcam

app = FastAPI()
cam = Webcam()


@app.get("/")
async def root():
    html = open("index.html").read()
    return HTMLResponse(html)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        async for rgb_encoded, gray_encoded, blue_encoded in cam.process_live_feed():
            # returning rgb as bgr because web browsers will auto convert bgr to rgb.
            # So this basically tricks the browser to display bgr
            await websocket.send_text(
                f'{{"bgr": "{rgb_encoded}", '
                f'"gray": "{gray_encoded}", '
                f'"blue": "{blue_encoded}"}}'
            )
    except WebSocketDisconnect:
        print("Websocket disconnected!")
    finally:
        cam.stop()


@app.websocket("/ws/cache")
async def websocket_cache(websocket: WebSocket):
    await websocket.accept()
    print("Fetching from cache")
    try:
        async for frame in cam.process_cache_feed():
            await websocket.send_text(
                f'{{"bgr": "{frame[1]}", "gray": "{frame[2]}", "blue": "{frame[3]}"}}'
            )
    except WebSocketDisconnect:
        print("Websocket disconnected")
    except Exception as ex:
        print(ex)
    if websocket.application_state != WebSocketState.DISCONNECTED:
        await websocket.close()
