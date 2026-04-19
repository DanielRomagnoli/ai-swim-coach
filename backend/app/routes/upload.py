from fastapi import APIRouter
from fastapi.responses import FileResponse
import uuid
import requests
import os

from app.services.pipeline import run_pipeline

router = APIRouter()

VIDEO_STORE = {}
BASE_DIR = "/opt/render/project/src/backend/processed"
os.makedirs(BASE_DIR, exist_ok=True)


@router.post("/upload-url")
async def upload_from_url(data: dict):
    video_url = data["url"]

    input_path = f"/tmp/{uuid.uuid4()}.mp4"
    video_id = str(uuid.uuid4())

    base_path = f"{BASE_DIR}/{video_id}.mp4"
    final_path = f"{BASE_DIR}/{video_id}_final.mp4"

    # download video
    r = requests.get(video_url)
    with open(input_path, "wb") as f:
        f.write(r.content)

    # 🔥 RUN EVERYTHING SYNCHRONOUSLY
    result = run_pipeline(input_path, base_path)

    if not os.path.exists(final_path):
        raise RuntimeError("Video not created")

    VIDEO_STORE[video_id] = final_path

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

    return FileResponse(
        path,
        media_type="video/mp4",
        headers={
            "Content-Disposition": "inline",
            "Accept-Ranges": "bytes"
        }
    )