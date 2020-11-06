from fastapi import FastAPI
from obj_detection import router as obj_routes

app = FastAPI()

app.include_router(
    obj_routes,
    tags=["Object Detection"],
    prefix="/detection",
    responses={ 404: {"description": "Not found"} },
)