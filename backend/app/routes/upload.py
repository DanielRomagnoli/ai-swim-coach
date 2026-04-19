from fastapi import APIRouter
from fastapi.responses import FileResponse
import uuid
import requests
import os
import threading

from app.services.pipeline import process_video_only, run_ai_only

router = APIRouter()

VIDEO_STORE = {}
STATUS_STORE = {}

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

    # 🔥 STEP 1: FAST video processing ONLY
    metrics = process_video_only(input_path, base_path)

    if not os.path.exists(final_path):
        raise RuntimeError("Video processing failed")

    VIDEO_STORE[video_id] = final_path

    # initial status
    STATUS_STORE[video_id] = {
        "status": "processing_ai",
        "metrics": metrics,
        "video_url": f"/video/{video_id}"
    }

    # 🔥 STEP 2: run AI async (non-blocking)
    def run_ai():
        try:
            print("Starting AI for", video_id)

            result = run_ai_only(metrics)

            STATUS_STORE[video_id] = {
                "status": "done",
                "video_url": f"/video/{video_id}",
                "metrics": result["metrics"],
                "feedback": result["feedback"],
                "drills": result["drills"],
                "practice": result["practice"],
            }

            print("AI DONE", video_id)

        except Exception as e:
            STATUS_STORE[video_id] = {
                "status": "error",
                "error": str(e)
            }

    threading.Thread(target=run_ai).start()

    return {
        "video_id": video_id,
        "video_url": f"/video/{video_id}",
        "metrics": metrics
    }


@router.get("/status/{video_id}")
def get_status(video_id: str):
    data = STATUS_STORE.get(video_id, {"status": "processing"})

    print("STATUS CHECK:", video_id, data["status"])

    return data


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