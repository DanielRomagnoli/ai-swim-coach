from app.services.pose import process_video_and_extract_metrics
from app.services.coach import full_analysis

import subprocess
import uuid


# ------------------------
# FAST VIDEO PROCESSING
# ------------------------
def process_video_only(input_path, output_path):
    temp_small = f"/tmp/small_{uuid.uuid4()}.mp4"

    # 🔥 SAFE + FAST ffmpeg
    result = subprocess.run([
        "ffmpeg",
        "-y",
        "-i", input_path,
        "-vf", "scale=320:-2,fps=30,format=yuv420p",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        temp_small
    ], capture_output=True, text=True)

    if result.returncode != 0:
        print("FFMPEG ERROR:", result.stderr)
        raise RuntimeError("FFmpeg failed")

    # 🔥 CV + metrics
    metrics = process_video_and_extract_metrics(temp_small, output_path)

    # 🔥 FINAL encode (fast + streamable)
    final_output = output_path.replace(".mp4", "_final.mp4")

    subprocess.run([
        "ffmpeg",
        "-y",
        "-i", output_path,
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "28",
        "-movflags", "+faststart",
        final_output
    ], check=True)

    return metrics


# ------------------------
# AI ONLY (ASYNC)
# ------------------------
def run_ai_only(metrics):
    result = full_analysis(metrics)

    return {
        "metrics": metrics,
        "feedback": result["feedback"],
        "drills": result["drills"],
        "practice": result["practice"],
    }