from app.services.pose import process_video_and_extract_metrics
from app.services.coach import analyze_metrics, generate_feedback, suggest_drills, generate_practice
import os
import subprocess


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "processed")


def run_pipeline(input_path, output_path):
    # Step 1: CV + metrics
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_name = output_path.split("/")[-1]
    output_path = os.path.join(PROCESSED_DIR, output_name)

    metrics = process_video_and_extract_metrics(input_path, output_path)

    # Step 2: analyze issues
    issues = analyze_metrics(metrics)

    # Step 3: generate feedback
    feedback = generate_feedback(issues)

    # Step 4: drills
    drills = suggest_drills(issues)

    # Step 5: practice
    practice = generate_practice(issues)

    final_output = output_path.replace(".mp4", "_final.mp4")

    subprocess.run([
    "ffmpeg",
    "-i", output_path,
    "-vcodec", "libx264",
    "-acodec", "aac",
    final_output
    ])

    output_name = os.path.basename(final_output)

    return {
        "metrics": metrics,
        "issues": issues,
        "feedback": feedback,
        "drills": drills,
        "practice": practice,
        "processed_video": output_name
    }




