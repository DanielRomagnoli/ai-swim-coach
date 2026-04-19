from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import FileResponse
import uuid
import requests
import os

from app.services.pipeline import process_video_only
from app.services.pipeline import run_ai_only

router = APIRouter()

BASE_DIR = "/opt/render/project/src/backend/processed"
os.makedirs(BASE_DIR, exist_ok=True)

RESULT_STORE = {}

# ------------------------
# STEP 1: FAST RESPONSE
# ------------------------
@router.post("/upload-url")
async def upload_from_url(data: dict, background_tasks: BackgroundTasks):
    video_url = data["url"]

    video_id = str(uuid.uuid4())
    input_path = f"/tmp/{video_id}.mp4"
    base_path = f"{BASE_DIR}/{video_id}.mp4"
    final_path = f"{BASE_DIR}/{video_id}_final.mp4"

    # download
    r = requests.get(video_url)
    with open(input_path, "wb") as f:
        f.write(r.content)

    # 🔥 STEP 1: FAST video processing ONLY
    metrics = process_video_only(input_path, base_path)

    if not os.path.exists(final_path):
        raise RuntimeError("Video processing failed")

    # 🔥 store initial state
    RESULT_STORE[video_id] = {
    "status": "processing_ai",
    "video_url": f"/video/{video_id}",
    "metrics": metrics   # 🔥 store it
    }
    # 🔥 STEP 2: run AI in background
    background_tasks.add_task(run_ai_background, video_id, metrics)

    return {
        "video_id": video_id,
        "video_url": f"/video/{video_id}"
    }


# ------------------------
# BACKGROUND AI
# ------------------------
def run_ai_background(video_id, metrics):
    try:
        result = run_ai_only(metrics)

        RESULT_STORE[video_id] = {
            "status": "done",
            "video_url": f"/video/{video_id}",
            "metrics": result["metrics"],
            "feedback": result["feedback"],
            "drills": result["drills"],
            "practice": result["practice"],
        }

    except Exception as e:
        RESULT_STORE[video_id] = {
            "status": "error",
            "error": str(e)
        }

# ------------------------
# STATUS ENDPOINT
# ------------------------
@router.get("/status/{video_id}")
def get_status(video_id: str):
    return RESULT_STORE.get(video_id, {"status": "processing"})


# ------------------------
# VIDEO SERVE
# ------------------------
@router.get("/video/{video_id}")
def get_video(video_id: str):
    path = f"{BASE_DIR}/{video_id}_final.mp4"

    if not os.path.exists(path):
        return {"error": "Video not found"}

    return FileResponse(
        path,
        media_type="video/mp4",
        headers={
            "Content-Disposition": "inline",
            "Accept-Ranges": "bytes"
        }
    )