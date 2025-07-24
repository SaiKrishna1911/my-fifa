import base64
import json
import os
from typing import List, Dict, Any, Optional
import re

import cv2
import mediapipe as mp
import numpy as np
from openai import OpenAI

# --- New Imports and Lazy Classifier ---
from PIL import Image
from transformers import AutoImageProcessor, SiglipForImageClassification
import torch

# Lazy singleton classifier (loads on first call)
_processor = None
_model = None
def _get_classifier():
    """Lazy‑load the fine‑tuned Hugging Face model for gym‑exercise recognition."""
    global _processor, _model
    if _processor is None or _model is None:
        _processor = AutoImageProcessor.from_pretrained(
            "prithivMLmods/Gym-Workout-Classifier-SigLIP2"
        )
        _model = SiglipForImageClassification.from_pretrained(
            "prithivMLmods/Gym-Workout-Classifier-SigLIP2"
        )
        _model.eval()
    return _processor, _model

from utils.clients import sync_client

mp_pose = mp.solutions.pose.Pose(static_image_mode=True)
# --- Helper: classify_exercise_from_frames ---
from collections import Counter

def _normalize(text: str) -> str:
    return re.sub(r"[^a-z]", "", text.lower())


def classify_exercise_from_frames(frames: List[np.ndarray], top_k: int = 3) -> str:
    """
    Predict exercise label from a few sampled frames using the SigLIP model.
    Returns the majority‑vote label (lower‑case).
    """
    processor, model = _get_classifier()
    preds = []
    for frame in frames[:top_k]:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb)
        inputs = processor(images=pil_img, return_tensors="pt")
        with torch.no_grad():
            logits = model(**inputs).logits
        label_id = int(torch.softmax(logits, dim=-1).argmax(dim=-1))
        # id2label keys are integers, not strings
        label = model.config.id2label.get(label_id, "unknown")
        preds.append(label.lower())
    if not preds:
        return "unknown"
    return Counter(preds).most_common(1)[0][0]


def _extract_keyframes(video_bytes: bytes, every_n: int = 6) -> List[np.ndarray]:
    """Grab every N-th frame from the clip (returns BGR numpy arrays). Handles both video and GIF."""
    tmp = "/tmp/_clip.mp4"
    with open(tmp, "wb") as fh:
        fh.write(video_bytes)

    # Ensure the output directory exists
    os.makedirs("/tmp/frames/", exist_ok=True)

    frames = []
    cap = cv2.VideoCapture(tmp)
    if cap.isOpened():
        idx = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            if idx % every_n == 0:
                frames.append(frame)
                # Save the frame as an image file
                cv2.imwrite(f"/tmp/frames/frame_{idx:03d}.jpg", frame)
            idx += 1
        cap.release()
        return frames
    else:
        # Attempt to load as a GIF using PIL
        try:
            from PIL import Image, ImageSequence
            pil_img = Image.open(tmp)
            for i, frame in enumerate(ImageSequence.Iterator(pil_img)):
                if i % every_n == 0:
                    rgb_frame = frame.convert("RGB")
                    np_frame = np.array(rgb_frame)
                    bgr_frame = cv2.cvtColor(np_frame, cv2.COLOR_RGB2BGR)
                    frames.append(bgr_frame)
                    cv2.imwrite(f"/tmp/frames/frame_{i:03d}.jpg", bgr_frame)
            return frames
        except Exception as e:
            raise RuntimeError(f"Failed to extract frames from video or GIF: {e}")


def _angle(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> float:
    """Angle ABC (degrees) with vertex at B."""
    ba, bc = a - b, c - b
    cos = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
    return float(np.degrees(np.arccos(np.clip(cos, -1.0, 1.0))))


def _landmarks(frame: np.ndarray) -> Optional[Dict[str, np.ndarray]]:
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    res = mp_pose.process(rgb)
    if not res.pose_landmarks:
        return None
    h, w = frame.shape[:2]
    lm = res.pose_landmarks.landmark
    get = lambda p: np.array([lm[p].x * w, lm[p].y * h])
    return {
        "hip": get(mp.solutions.pose.PoseLandmark.LEFT_HIP),
        "knee": get(mp.solutions.pose.PoseLandmark.LEFT_KNEE),
        "ankle": get(mp.solutions.pose.PoseLandmark.LEFT_ANKLE),
        "shoulder": get(mp.solutions.pose.PoseLandmark.LEFT_SHOULDER),
    }


def _frame_angles(frame: np.ndarray) -> Optional[Dict[str, float]]:
    lm = _landmarks(frame)
    if not lm:
        return None
    knee = _angle(lm["hip"], lm["knee"], lm["ankle"])
    hip = _angle(lm["shoulder"], lm["hip"], lm["knee"])
    back = _angle(lm["hip"], lm["shoulder"], lm["shoulder"] + np.array([0, -100]))
    return {
        "knee_angle": round(knee, 1),
        "hip_angle": round(hip, 1),
        "back_angle": round(back, 1),
    }


# ------------------------------------------------------------------- #
# GPT feedback
# ------------------------------------------------------------------- #
def _gpt_feedback(exercise: str, snapshots: List[Dict[str, float]]) -> str:
    prompt = f"""
You are a certified strength coach. Analyse the user's {exercise} based on these joint
angle snapshots (degrees) from multiple video frames:

{snapshots}

Based on the snap shot, if the exercise seems to be invalid, please feel free to say that the upload clip doesn't suit the exercise mentioned.
Return **JSON only**:
{{
  "ok": true,
  "exercise": "...",
  "issues": [
    {{ "metric": "knee_angle", "frame": 1, "value": 155, "ideal": "90–130", "advice": "..." }},
    ...
  ],
  "summary": "short friendly summary"
}}
"""
    resp = sync_client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "You output JSON only, no prose."},
            {"role": "user", "content": prompt.strip()},
        ],
    )
    return resp.choices[0].message.content.strip()

def _gpt_estimates(exercise: str, snapshots: List[Dict[str, float]]) -> Dict[str, Any]:
    prompt = f"""
You're a fitness assistant. Based on the user's exercise: **{exercise}**, and the following posture data (joint angles per frame), estimate:

- How many reps were performed?
- Approximate calories burned?
- Estimated peak heart rate during the set?

Return **strict JSON** with this format only:
{{
  "reps": 0,
  "calories_burned": 0.0,
  "estimated_heart_rate": 0
}}

📹 🔥 VIDEO RULE (Important!):
- If the user asks:  
  - “How do I do ___?”  
  - “Show me ___”  
  - Or anything that implies they need help doing the exercise…  
  👉 **Immediately respond with a helpful YouTube video link** to that exercise, no follow-up required.
- You may describe it briefly, but **always include a valid video link** in that response.
- U can always prompt the user to upload a video clip for duration 3-5 seconds and when he does redirect to the `validate_posture` method.
- If the user uploads a video or mentions reviewing form, push-up quality, etc., you should decide whether to call the `validate_posture` tool with the clip and the relevant exercise.
- Make sure to return `"exercise"` field with a canonical name like "push-up", "squat", etc., to help downstream posture analysis.
- Estimate the number of reps performed if video is available and include that in `"reps"` key.
- Also include `"calories_burned"` and `"estimated_heart_rate"` fields with approximate values based on video and context.

Posture snapshots:
{json.dumps(snapshots, indent=2)}
"""
    resp = sync_client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "You return only JSON, no explanations."},
            {"role": "user", "content": prompt.strip()}
        ]
    )
    return json.loads(resp.choices[0].message.content.strip())

def validate_posture(exercise: str, video_b64: str) -> Dict[str, Any]:
    # Handle raw filename fallback (GIF, etc.)
    if video_b64.strip().lower() not in ("<user_file>", "<file_bytes>") and not video_b64.strip().startswith(("data:", "base64,", "/9j", "iVB", "AAAA")) and not re.match(r"^[A-Za-z0-9+/=]+$", video_b64.strip()):
        print("Treating input as a local filename:", video_b64)
        try:
            with open(video_b64.strip(), "rb") as fh:
                video_bytes = fh.read()
        except FileNotFoundError:
            return {
                "ok": False,
                "exercise": exercise,
                "summary": f"Could not find uploaded file: '{video_b64.strip()}'"
            }
    else:
        # Add padding if necessary to base64 string before decoding
        video_b64 += '=' * (-len(video_b64) % 4)
        video_bytes = base64.b64decode(video_b64)
    frames = _extract_keyframes(video_bytes)

    # Step 1: Visual classification of exercise from frames
    predicted_exercise = classify_exercise_from_frames(frames)

    # Step 2: If mismatch, short-circuit the response
    if _normalize(predicted_exercise) != _normalize(exercise):
        return {
            "ok": False,
            "exercise": exercise,
            "predicted": predicted_exercise,
            "summary": f"Provider video doesn't match with the given exercise - '{exercise}'. Skipping validation."
        }

    # Step 3: Proceed with normal posture validation
    snapshots = [a for f in frames if (a := _frame_angles(f))]
    if not snapshots:
        return {
            "ok": False,
            "exercise": exercise,
            "summary": "No landmarks detected. Try a clearer, full-body clip."
        }

    fitness_stats = _gpt_estimates(exercise, snapshots)
    raw_json = _gpt_feedback(exercise, snapshots)
    try:
        result = json.loads(raw_json)
        result.update(fitness_stats)
    except Exception:
        result = {
            "ok": True,
            "exercise": exercise,
            "angles": snapshots,
            "feedback": raw_json,
        }
        result.update(fitness_stats)
    # Instead of returning here, just return the full detailed result dictionary
    return result