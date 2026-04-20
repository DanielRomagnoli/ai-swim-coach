import os
import numpy as np


# -------------------------
# SMOOTHING
# -------------------------
def smooth_signal(signal, window_size=15):
    if len(signal) < window_size:
        return signal
    return np.convolve(signal, np.ones(window_size)/window_size, mode='valid')


# -------------------------
# PEAK DETECTION
# -------------------------
def detect_peaks(signal, fps):
    peaks = []

    threshold = np.mean(signal) - 0.01
    min_distance = int(fps * 0.4)

    for i in range(1, len(signal)-1):
        if (
            signal[i] > signal[i-1] and
            signal[i] > signal[i+1] and
            signal[i] > threshold
        ):
            if not peaks or i - peaks[-1] > min_distance:
                peaks.append(i)

    return peaks


# -------------------------
# MAIN PIPELINE
# -------------------------
def process_video_and_extract_metrics(input_path: str, output_path: str):
    import cv2
    import mediapipe as mp

    cap = cv2.VideoCapture(input_path)

    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils

    fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30

    target_width = 640
    target_height = 360

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (target_width, target_height))

    right_wrist_y = []
    left_wrist_y = []
    hip_diff = []
    head_diff = []

    with mp_pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    ) as pose:

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.resize(frame, (target_width, target_height))
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            results = pose.process(rgb)

            if results.pose_landmarks:
                lm = results.pose_landmarks.landmark

                mp_drawing.draw_landmarks(
                    frame,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS
                )

                try:
                    rw = lm[mp_pose.PoseLandmark.RIGHT_WRIST.value]
                    lw = lm[mp_pose.PoseLandmark.LEFT_WRIST.value]

                    ls = lm[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
                    rs = lm[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]

                    lh = lm[mp_pose.PoseLandmark.LEFT_HIP.value]
                    rh = lm[mp_pose.PoseLandmark.RIGHT_HIP.value]

                    nose = lm[mp_pose.PoseLandmark.NOSE.value]

                    if rw.visibility < 0.5 or lw.visibility < 0.5:
                        continue

                    right_wrist_y.append(rw.y)
                    left_wrist_y.append(lw.y)

                    shoulder = (ls.y + rs.y) / 2
                    hip = (lh.y + rh.y) / 2
                    torso = abs(ls.y - lh.y) + 1e-6

                    head_diff.append((nose.y - shoulder) / torso)
                    hip_diff.append((hip - shoulder) / torso)

                except:
                    continue

            out.write(frame)

    cap.release()
    out.release()
    cv2.destroyAllWindows()

    if len(right_wrist_y) < 20:
        return {"error": "Not enough data"}

    right = smooth_signal(np.array(right_wrist_y))
    left = smooth_signal(np.array(left_wrist_y))

    r_peaks = detect_peaks(right, fps)
    l_peaks = detect_peaks(left, fps)

    duration = len(right) / fps

    # -------------------------
    # STROKE RATE
    # -------------------------
    stroke_rate = (len(r_peaks) / duration) * 60 if duration > 0 else 0
    stroke_rate = float(np.clip(stroke_rate, 20, 100))

    # -------------------------
    # SYMMETRY (0–1)
    # -------------------------
    symmetry = 1.0
    if len(r_peaks) > 1 and len(l_peaks) > 1:
        r_int = np.diff(r_peaks)
        l_int = np.diff(l_peaks)

        n = min(len(r_int), len(l_int))
        if n > 0:
            ratios = [min(r_int[i], l_int[i]) / (max(r_int[i], l_int[i]) + 1e-6) for i in range(n)]
            symmetry = float(np.mean(ratios))

    # -------------------------
    # ALTERNATION (0–1)
    # -------------------------
    alternation = 1.0
    if len(r_peaks) > 0 and len(l_peaks) > 0:
        scores = []
        for r in r_peaks:
            closest = min(l_peaks, key=lambda x: abs(x - r))
            diff = abs(r - closest) / fps
            scores.append(np.exp(-diff))
        alternation = float(np.mean(scores))

    # -------------------------
    # CONSISTENCY (0–1)
    # -------------------------
    consistency = 1.0
    if len(r_peaks) > 2:
        intervals = np.diff(r_peaks) / fps
        consistency = float(np.exp(-np.std(intervals)))

    # -------------------------
    # BODY + HEAD
    # -------------------------
    body_position = float(np.clip(1 - abs(np.mean(hip_diff)), 0, 1))
    head_position = float(np.clip(1 - abs(np.mean(head_diff)), 0, 1))

    return {
        "stroke_rate": stroke_rate,
        "symmetry": symmetry,
        "alternation": alternation,
        "consistency": consistency,
        "body_position": body_position,
        "head_position": head_position
    }