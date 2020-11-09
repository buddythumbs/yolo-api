import io
import cv2
import numpy as np
import os
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, WebSocket
from fastapi.responses import FileResponse, HTMLResponse
from obj_detection.object_detection import ObjectRecognizer
from starlette.responses import StreamingResponse

recog = ObjectRecognizer(write=True)

router = APIRouter()

@router.post("/image")
async def detect_image(file: UploadFile = File(...)):
    contents = await file.read()
    img = cv2.imdecode(np.fromstring(contents, np.uint8), cv2.IMREAD_UNCHANGED)
    detections = recog.detect_objects_in_image(img, load=False, name=file.filename)
    return { "file_name": file.filename, "detections": detections }

@router.post("/video")
async def detect_video(file: UploadFile = File(...)):
    contents = await file.read()
    file_saviour = f'{recog.ARTIFACTS_DIR}uploaded_{file.filename}'
    
    with open(file_saviour, 'wb') as vid:
        vid.write(contents)

    detections = recog.detect_objects_in_video(file=file_saviour, name=file.filename)

    return { "file_name": file.filename, 'saved': True, "detections": detections }

@router.get("/processed_files/{filename}")
def send_file(filename: str):
    return FileResponse(f'{recog.ARTIFACTS_DIR}/{filename}')

@router.get("/processed_files/")
def list_files():
    entries = os.listdir(f'{recog.ARTIFACTS_DIR}/')
    return {"files" : entries }


# Websocket Route
ws_router = APIRouter()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:80/ws/message");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""

@ws_router.get("/")
def ws_hook_up():
    return HTMLResponse(html)

@ws_router.websocket("/message")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")