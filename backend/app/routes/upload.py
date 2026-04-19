from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import FileResponse
import uuid
import requests
import os

from app.services.pipeline import run_pipeline

router = APIRouter()

BASE_DIR = "/opt/render/project/src/backend/processed"
os.makedirs(BASE_DIR, exist_ok=True)

import json

STATUS_DIR = "/tmp/status"
os.makedirs(STATUS_DIR, exist_ok=True)

def save_status(video_id, data):
    with open(f"{STATUS_DIR}/{video_id}.json", "w") as f:
        json.dump(data, f)

def load_status(video_id):
    path = f"{STATUS_DIR}/{video_id}.json"
    if not os.path.exists(path):
        return {"status": "not_found"}
    with open(path) as f:
        return json.load(f)
    

def process_video(video_id, input_path, base_path):
    try:
        result = run_pipeline(input_path, base_path)

        final_path = base_path.replace(".mp4", "_final.mp4")

        if not os.path.exists(final_path):
            raise RuntimeError("Processed video not created")

        if os.path.getsize(final_path) < 100000:
            raise RuntimeError("Video corrupted")

        
        save_status(video_id, {
    "status": "done",
    "metrics": result["metrics"],
    "feedback": result["feedback"],
    "drills": result["drills"],
    "practice": result["practice"],
    "video_url": f"/video/{video_id}"
})

    except Exception as e:
        print("PIPELINE ERROR:", e)


@router.post("/upload-url")
async def upload_from_url(data: dict, background_tasks: BackgroundTasks):
    video_url = data["url"]

    input_path = f"/tmp/{uuid.uuid4()}.mp4"
    video_id = str(uuid.uuid4())

    base_path = f"{BASE_DIR}/{video_id}.mp4"

    # download video
    r = requests.get(video_url)
    with open(input_path, "wb") as f:
        f.write(r.content)

    # 🔥 run in background (FAST RESPONSE)
    save_status(video_id, {"status": "processing"})
    background_tasks.add_task(process_video, video_id, input_path, base_path)

    return {
        "video_id": video_id,
        "status": "processing"
    }


@router.get("/status/{video_id}")
def get_status(video_id: str):
    return load_status(video_id)


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