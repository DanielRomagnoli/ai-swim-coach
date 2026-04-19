from fastapi import APIRouter
from fastapi.responses import FileResponse
import uuid
import requests
import os

from app.services.pipeline import run_pipeline

router = APIRouter()

# 🔥 simple in-memory store (fine for now)
VIDEO_STORE = {}


@router.post("/upload-url")
async def upload_from_url(data: dict):
    video_url = data["url"]

    # paths
    input_path = f"/tmp/{uuid.uuid4()}.mp4"
    video_id = str(uuid.uuid4())
    output_path = f"/tmp/{video_id}.mp4"

    # download video
    r = requests.get(video_url)
    with open(input_path, "wb") as f:
        f.write(r.content)

    # run pipeline
    result = run_pipeline(input_path, output_path)

    # 🔥 ensure file exists
    if not os.path.exists(output_path):
        raise RuntimeError("Processed video not created")

    # store for retrieval
    VIDEO_STORE[video_id] = output_path

    # return JSON + video URL
    return {
        "metrics": result["metrics"],
        "feedback": result["feedback"],
        "drills": result["drills"],
        "practice": result["practice"],
        "video_url": f"/video/{video_id}"
    }


@router.get("/video/{video_id}")
def get_video(video_id: str):
    path = VIDEO_STORE.get(video_id)

    if not path or not os.path.exists(path):
        return {"error": "Video not found"}

    return FileResponse(path, media_type="video/mp4")