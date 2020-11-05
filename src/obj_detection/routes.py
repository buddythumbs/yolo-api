from fastapi import APIRouter, HTTPException, Depends, File, UploadFile
from fastapi.responses import FileResponse
from obj_detection.object_detection import ObjectRecognizer
import cv2
import numpy as np

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
    file_saviour = f'outputs/uploaded_{file.filename}'
    
    with open(file_saviour, 'wb') as vid:
        vid.write(contents)

    detections = recog.detect_objects_in_video(file=file_saviour, name=file.filename)

    return { "file_name": file.filename, 'saved': True, "detections": detections }

@router.get("/processed_file/{filename}")
def send_file(filename: str):
    return FileResponse(f'outputs/DETECTED_{filename}')