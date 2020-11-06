from fastapi import FastAPI
from obj_detection import router as obj_routes
from obj_detection import ws_router

app = FastAPI()

app.include_router(
    obj_routes,
    tags=["Object Detection"],
    prefix="/detection",
    responses={ 404: {"description": "Not found"} },
)

app.include_router(
    ws_router,
    tags=["WS Hookup"],
    prefix="/ws",
    responses={ 404: {"description": "Not found"} },
)