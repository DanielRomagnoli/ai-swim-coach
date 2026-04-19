
import os
import numpy as np


def smooth_signal(signal, window_size=25):
    return np.convolve(signal, np.ones(window_size)/window_size, mode='valid')


def detect_peaks(signal, fps):
    peaks = []
    threshold = np.mean(signal) + 0.02
    min_distance = int(fps * 0.6)

    for i in range(1, len(signal)-1):
        if (
            signal[i] > signal[i-1] and
            signal[i] > signal[i+1] and
            signal[i] > threshold
        ):
            if not peaks or i - peaks[-1] > min_distance:
                peaks.append(i)

    return peaks


def process_video_and_extract_metrics(input_path: str, output_path: str):
    import cv2
    import mediapipe as mp
    import numpy as np

    cap = cv2.VideoCapture(input_path)

    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils

    fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30

    # ↓↓↓ reduce resolution (HUGE memory win)
    target_width = 640
    target_height = 360

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (target_width, target_height))

    # only store minimal signals
    right_wrist_y = []
    left_wrist_y = []
    hip_diff = []
    head_diff = []

    frame_count = 0

    with mp_pose.Pose(
        static_image_mode=False,
        model_complexity=0,  # lighter model
        enable_segmentation=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    ) as pose:

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1

            # ↓↓↓ skip frames (HUGE performance gain)
            # if frame_count % 3 != 0:
            #     continue

            # ↓↓↓ resize frame
            frame = cv2.resize(frame, (target_width, target_height))

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(rgb)

            if results.pose_landmarks:
                lm = results.pose_landmarks.landmark

                # draw skeleton
                mp_drawing.draw_landmarks(
                    frame,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS
                )

                try:
                    nose = lm[mp_pose.PoseLandmark.NOSE.value]
                    rw = lm[mp_pose.PoseLandmark.RIGHT_WRIST.value]
                    lw = lm[mp_pose.PoseLandmark.LEFT_WRIST.value]

                    ls = lm[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
                    rs = lm[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]

                    lh = lm[mp_pose.PoseLandmark.LEFT_HIP.value]
                    rh = lm[mp_pose.PoseLandmark.RIGHT_HIP.value]

                    # skip low visibility frames
                    if rw.visibility < 0.5 or lw.visibility < 0.5:
                        continue

                    # signals
                    right_wrist_y.append(rw.y)
                    left_wrist_y.append(lw.y)

                    shoulder_y = (ls.y + rs.y) / 2
                    torso_length = abs(ls.y - lh.y) + 1e-6

                    head_y = nose.y
                    hip_y = (lh.y + rh.y) / 2

                    head_diff.append((head_y - shoulder_y) / torso_length)
                    hip_diff.append((hip_y - shoulder_y) / torso_length)

                except:
                    continue

            out.write(frame)

    cap.release()
    out.release()

    # ---------- METRICS ----------

    if len(right_wrist_y) < 10:
        return {"error": "Not enough data"}

    right_signal = np.array(right_wrist_y)
    left_signal = np.array(left_wrist_y)

    right_smooth = smooth_signal(right_signal)
    left_smooth = smooth_signal(left_signal)

    right_peaks = detect_peaks(right_smooth, fps)
    left_peaks = detect_peaks(left_smooth, fps)

    duration_seconds = len(right_smooth) / fps

    stroke_rate = len(right_peaks) / duration_seconds * 60 if duration_seconds > 0 else 0

    right_intervals = np.diff(right_peaks) / fps if len(right_peaks) > 1 else []
    left_intervals = np.diff(left_peaks) / fps if len(left_peaks) > 1 else []

    # symmetry
    symmetry_score = 0
    if len(right_intervals) > 0 and len(left_intervals) > 0:
        right_times = [(right_peaks[i] + right_peaks[i+1]) / 2 for i in range(len(right_peaks)-1)]
        left_times = [(left_peaks[i] + left_peaks[i+1]) / 2 for i in range(len(left_peaks)-1)]

        diffs = []
        for rt, ri in zip(right_times, right_intervals):
            idx = np.argmin([abs(rt - lt) for lt in left_times])
            li = left_intervals[idx]
            diffs.append(abs(ri - li) / ((ri + li) / 2 + 1e-6))

        symmetry_score = np.mean(diffs)

    # alternation
    alternation_score = 0
    if len(left_peaks) > 0:
        alternation_diffs = [
            abs(r - min(left_peaks, key=lambda l: abs(l - r)))
            for r in right_peaks
        ]
        alternation_score = np.mean(alternation_diffs) / fps

    # stroke type
    intervals = np.diff(right_peaks) / fps if len(right_peaks) > 1 else []
    mean_interval = np.mean(intervals) if len(intervals) > 0 else 0

    stroke_type = "catch-up" if mean_interval > 1.2 else "normal"

    # posture
    head_lift_score = float(np.mean(head_diff)) if len(head_diff) > 0 else 0
    hip_sinking_score = float(np.mean(hip_diff)) if len(hip_diff) > 0 else 0

    return {
        "stroke_rate": float(stroke_rate),
        "symmetry": float(symmetry_score),
        "alternation": float(alternation_score),
        "hip": float(hip_sinking_score),
        "head": float(head_lift_score),
        "stroke_type": stroke_type
    }