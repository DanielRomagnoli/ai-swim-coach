from app.services.pose import process_video_and_extract_metrics
from app.services.coach import full_analysis

import os
import subprocess
import uuid


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "processed")

def process_video_only(input_path, output_path):
    import subprocess, uuid

    temp_small = f"/tmp/small_{uuid.uuid4()}.mp4"

    subprocess.run([
        "ffmpeg",
        "-y",
        "-i", input_path,
        "-vf", "scale=320:-1,fps=30",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-movflags", "+faststart",
        temp_small
    ], check=True)

    # 🔥 THIS already gives metrics
    metrics = process_video_and_extract_metrics(temp_small, output_path)

    final_output = output_path.replace(".mp4", "_final.mp4")

    subprocess.run([
        "ffmpeg",
        "-y",
        "-i", output_path,
        "-vcodec", "libx264",
        "-preset", "ultrafast",
        "-movflags", "+faststart",
        final_output
    ], check=True)

    return metrics


def run_ai_only(metrics):
    from app.services.coach import (
        analyze_metrics,
        generate_feedback,
        suggest_drills,
        generate_practice,
        full_analysis
    )

    result = full_analysis(metrics)
    return {
        "metrics": metrics,
        "feedback": result["feedback"],
        "drills": result["drills"],
        "practice": result["practice"],
    }

def run_pipeline(input_path, output_path):

    # 🔥 STEP 1: Downscale + reduce FPS (FAST)
    temp_small_path = f"/tmp/small_{uuid.uuid4()}.mp4"

    subprocess.run([
    "ffmpeg",
    "-y",
    "-i", input_path,
    "-vf", "scale=320:trunc(ow/a/2)*2,fps=30,format=yuv420p",
    "-c:v", "libx264",
    "-preset", "ultrafast",
    "-pix_fmt", "yuv420p",
    temp_small_path
    ], check=True)

    # Use smaller video for ALL processing
    processed_input = temp_small_path


    # 🔥 STEP 2: Run CV + metrics (this should also write video)
    metrics = process_video_and_extract_metrics(processed_input, output_path)


    analysis = generate_full_analysis(metrics)

    issues = analysis["issues"]
    feedback = analysis["feedback"]
    drills = analysis["drills"]
    practice = analysis["practice"]


    # 🔥 STEP 4: FINAL FAST ENCODE (ONLY ONCE)
    final_output = output_path.replace(".mp4", "_final.mp4")

    subprocess.run([
        "ffmpeg",
        "-y",
        "-i", output_path,
        "-c:v", "libx264",
        "-preset", "ultrafast",       # 🔥 SPEED
        "-crf", "28",                 # slight compression
        "-movflags", "+faststart",   # 🔥 STREAMING FIX
        final_output
    ], check=True)


    # 🔥 Return only FINAL video
    output_name = os.path.basename(final_output)

    return {
        "metrics": metrics,
        "issues": issues,
        "feedback": feedback,
        "drills": drills,
        "practice": practice,
        "processed_video": output_name
    }