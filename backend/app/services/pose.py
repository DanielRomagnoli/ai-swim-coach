import cv2
import mediapipe as mp
import os
import numpy as np
import matplotlib.pyplot as plt

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils


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
    cap = cv2.VideoCapture(input_path)

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    if fps == 0:
        fps = 30

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    keypoints_over_time = []


    with mp_pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        enable_segmentation=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    ) as pose:

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(rgb)

            if results.pose_landmarks:
                mp_drawing.draw_landmarks(
                    frame,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS
                )
                wrist = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST.value]
                if wrist.visibility < 0.5:
                    continue

                frame_data = {}

                for i, landmark in enumerate(results.pose_landmarks.landmark):
                    frame_data[i] = {
                        "x": landmark.x,
                        "y": landmark.y,
                        "z": landmark.z
                    }

                keypoints_over_time.append(frame_data)

            out.write(frame)

    cap.release()
    out.release()

    right_wrist_y = []
    left_wrist_y = []
    hip_diff = []
    head_diff = []

    for frame in keypoints_over_time:
        nose = frame[mp_pose.PoseLandmark.NOSE.value]
        right = frame[mp_pose.PoseLandmark.RIGHT_WRIST.value]
        left = frame[mp_pose.PoseLandmark.LEFT_WRIST.value]

        right_wrist_y.append(right["y"])
        left_wrist_y.append(left["y"])
        left_shoulder = frame[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        right_shoulder = frame[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]

        left_hip = frame[mp_pose.PoseLandmark.LEFT_HIP.value]
        right_hip = frame[mp_pose.PoseLandmark.RIGHT_HIP.value]

        shoulder_y = (left_shoulder["y"] + right_shoulder["y"]) / 2
        torso_length = abs(left_shoulder["y"] - left_hip["y"])
        head_y = nose["y"]
        hip_y = (left_hip["y"] + right_hip["y"]) / 2
        normalized_hip = (hip_y - shoulder_y) / torso_length
        normalized_head = (head_y - shoulder_y) / torso_length
    
        head_diff.append(normalized_head)

        hip_diff.append(normalized_hip)

    head_diff = np.array(head_diff)
    head_lift_score = np.mean(head_diff)
    breath_variability = np.std(head_diff)
    hip_diff = np.array(hip_diff)

    hip_sinking_score = np.mean(hip_diff)   

    right_signal = np.array(right_wrist_y)
    left_signal = np.array(left_wrist_y)

    # Smooth signals
    right_smooth = smooth_signal(right_signal)
    left_smooth = smooth_signal(left_signal)

    # Detect peaks
    right_peaks = detect_peaks(right_smooth, fps)
    left_peaks = detect_peaks(left_smooth, fps)

    # Compute stroke rate
    duration_seconds = len(right_smooth) / fps
    stroke_rate = len(right_peaks) / duration_seconds * 60

    right_intervals = np.diff(right_peaks) / fps
    left_intervals  = np.diff(left_peaks) / fps

    # compute midpoints (time of each interval)
    right_times = [(right_peaks[i] + right_peaks[i+1]) / 2 for i in range(len(right_peaks)-1)]
    left_times  = [(left_peaks[i] + left_peaks[i+1]) / 2 for i in range(len(left_peaks)-1)]

    symmetry_diffs = []

    for rt, ri in zip(right_times, right_intervals):
        # find closest left interval in time
        idx = np.argmin([abs(rt - lt) for lt in left_times])
        li = left_intervals[idx]

        diff = abs(ri - li) / ((ri + li) / 2)
        symmetry_diffs.append(diff)

    symmetry_score = np.mean(symmetry_diffs)

    intervals = np.diff(right_peaks) / fps

    mean_interval = np.mean(intervals)
    std_interval = np.std(intervals)

    # heuristic
    if mean_interval > 1.2:
        stroke_type = "catch-up"
    else:
        stroke_type = "normal"

    alternation_diffs = []

    for r in right_peaks:
        closest_l = min(left_peaks, key=lambda l: abs(l - r))
        alternation_diffs.append(abs(r - closest_l))

    alternation_score = np.mean(alternation_diffs) / fps

    right_mean = np.mean(right_intervals)
    left_mean = np.mean(left_intervals)

    if right_mean > left_mean:
        weaker_side = "right"
    else:
        weaker_side = "left"

    # print(f"Stroke Rate: {stroke_rate:.2f} strokes/min")
    # print(f"Symmetry Score: {symmetry_score:.2f}")
    # print(f"Alternating Score: {alternation_score:.2f}")
    # print(f"Stroke Type: {stroke_type}" )
    # print(f"Head Diff: {head_lift_score}")
    # print(f"Hip Diff: {hip_sinking_score}")

    return {
        "stroke_rate": stroke_rate,
        "symmetry": symmetry_score,
        "alternation": alternation_score,
        "hip": hip_sinking_score,
        "head": head_lift_score,
        "stroke_type": stroke_type
    }