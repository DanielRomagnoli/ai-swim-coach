from app.services.pose import process_video_and_extract_metrics
from app.services.coach import analyze_metrics, generate_feedback, suggest_drills, generate_practice

import subprocess
import uuid
import os


def run_pipeline(input_path, output_path):

    temp_small = f"/tmp/small_{uuid.uuid4()}.mp4"

    # 🔥 FAST VIDEO PROCESSING
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

    metrics = process_video_and_extract_metrics(temp_small, output_path)

    issues = analyze_metrics(metrics)
    feedback = generate_feedback(issues)
    drills = suggest_drills(issues)
    practice = generate_practice(issues)

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

    return {
        "metrics": metrics,
        "feedback": feedback,
        "drills": drills,
        "practice": practice,
        "processed_video": os.path.basename(final_output)
    }