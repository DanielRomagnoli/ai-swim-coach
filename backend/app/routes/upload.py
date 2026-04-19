from fastapi import APIRouter, UploadFile, File
import os
import uuid
from app.services.pose import process_video_and_extract_metrics
from app.services.pipeline import run_pipeline
from fastapi.responses import FileResponse
from fastapi.responses import StreamingResponse
import io

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "temp")
PROCESSED_DIR = os.path.join(BASE_DIR, "processed")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

@router.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    unique_name = f"{uuid.uuid4()}_{file.filename}"
    input_path = os.path.join(UPLOAD_DIR, unique_name)

    with open(input_path, "wb") as f:
        f.write(await file.read())

    output_name = f"processed_{unique_name}"
    output_path = os.path.join(PROCESSED_DIR, output_name)

    result = run_pipeline(input_path, output_path)

    return result

import requests

@router.post("/upload-url")
async def upload_from_url(data: dict):
    import uuid

    video_url = data["url"]

    input_path = f"/tmp/{uuid.uuid4()}.mp4"
    output_path = f"/tmp/processed_{uuid.uuid4()}.mp4"

    # 🔥 download video
    r = requests.get(video_url)
    with open(input_path, "wb") as f:
        f.write(r.content)

    result = run_pipeline(input_path, output_path)

    with open(output_path, "rb") as f:
        video_bytes = f.read()

    return StreamingResponse(
        io.BytesIO(video_bytes),
        media_type="video/mp4"
    )