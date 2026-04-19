from app.services.pose import process_video_and_extract_metrics
import subprocess
import uuid
import os


def process_video_only(input_path, output_path):
    temp_small = f"/tmp/small_{uuid.uuid4()}.mp4"

    subprocess.run([
        "ffmpeg",
        "-y",
        "-i", input_path,
        "-vf", "scale=320:-2,fps=24",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-movflags", "+faststart",
        temp_small
    ], check=True)

    # CV + metrics
    metrics = process_video_and_extract_metrics(temp_small, output_path)

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


def run_ai_only(metrics):
    from app.services.coach import full_analysis
    return full_analysis(metrics)