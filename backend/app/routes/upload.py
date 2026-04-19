from fastapi import APIRouter
from fastapi.responses import FileResponse
import uuid
import requests
import os

from app.services.pipeline import run_pipeline

router = APIRouter()

# 🔥 simple in-memory store (fine for now)
VIDEO_STORE = {}
os.makedirs("/opt/render/project/src/backend/processed", exist_ok=True)

@router.post("/upload-url")
async def upload_from_url(data: dict):
    video_url = data["url"]

    # paths
    input_path = f"/tmp/{uuid.uuid4()}.mp4"
    video_id = str(uuid.uuid4())

    base_path = f"/opt/render/project/src/backend/processed/{video_id}.mp4"
    final_path = f"/opt/render/project/src/backend/processed/{video_id}_final.mp4"

    # download video
    r = requests.get(video_url)
    with open(input_path, "wb") as f:
        f.write(r.content)

    # run pipeline
    result = run_pipeline(input_path, base_path)

    # 🔥 ensure file exists
    if not os.path.exists(final_path):
        raise RuntimeError("Processed video not created")
    
    if os.path.getsize(final_path) < 100000:  # <100KB = broken
        raise RuntimeError("Video corrupted or empty")

    # store for retrieval
    VIDEO_STORE[video_id] = final_path

    # return JSON + video URL
    return {
        "metrics": result["metrics"],
        "feedback": result["feedback"],
        "drills": result["drills"],
        "practice": result["practice"],
        "video_url": f"/video/{video_id}"
    }

from fastapi.responses import FileResponse

@router.get("/video/{video_id}")
def get_video(video_id: str):
    path = VIDEO_STORE.get(video_id)

    if not path or not os.path.exists(path):
        return {"error": "Video not found"}

    return FileResponse(
        path,
        media_type="video/mp4",
        headers={
            "Content-Disposition": "inline",
            "Accept-Ranges": "bytes"
        }
    )