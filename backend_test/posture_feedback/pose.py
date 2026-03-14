"""
Extract pose keypoints from an image using MediaPipe Pose (legacy API).
Used when the client sends a frame (base64) instead of pre-computed keypoints.
"""

import base64
import io

try:
    import mediapipe as mp
    import numpy as np
    from PIL import Image
except ImportError:
    mp = None
    np = None
    Image = None

from .schemas import Keypoint

# MediaPipe Pose 33 landmark names (index -> name), legacy mp.solutions.pose.PoseLandmark
POSE_LANDMARK_NAMES = [
    "NOSE", "LEFT_EYE_INNER", "LEFT_EYE", "LEFT_EYE_OUTER",
    "RIGHT_EYE_INNER", "RIGHT_EYE", "RIGHT_EYE_OUTER",
    "LEFT_EAR", "RIGHT_EAR", "MOUTH_LEFT", "MOUTH_RIGHT",
    "LEFT_SHOULDER", "RIGHT_SHOULDER", "LEFT_ELBOW", "RIGHT_ELBOW",
    "LEFT_WRIST", "RIGHT_WRIST", "LEFT_PINKY", "RIGHT_PINKY",
    "LEFT_INDEX", "RIGHT_INDEX", "LEFT_THUMB", "RIGHT_THUMB",
    "LEFT_HIP", "RIGHT_HIP", "LEFT_KNEE", "RIGHT_KNEE",
    "LEFT_ANKLE", "RIGHT_ANKLE", "LEFT_HEEL", "RIGHT_HEEL",
    "LEFT_FOOT_INDEX", "RIGHT_FOOT_INDEX",
]


def image_base64_to_keypoints(image_base64: str) -> list[Keypoint]:
    """
    Decode base64 image, run MediaPipe Pose, return keypoints.
    Raises ImportError if mediapipe/pillow not installed, ValueError if no pose detected.
    """
    if mp is None or np is None or Image is None:
        raise ImportError("mediapipe, numpy, and pillow are required. pip install mediapipe numpy pillow")

    # Support raw base64 or data URL (data:image/jpeg;base64,...)
    s = image_base64.strip()
    if s.startswith("data:"):
        s = s.split(",", 1)[-1]
    raw = base64.b64decode(s)
    pil_img = Image.open(io.BytesIO(raw)).convert("RGB")
    img_np = np.array(pil_img)

    with mp.solutions.pose.Pose(static_image_mode=True, model_complexity=1, min_detection_confidence=0.5) as pose:
        result = pose.process(img_np)

    if not result.pose_landmarks:
        raise ValueError("No pose detected in image")

    keypoints = []
    for i, lm in enumerate(result.pose_landmarks.landmark):
        name = POSE_LANDMARK_NAMES[i] if i < len(POSE_LANDMARK_NAMES) else f"LANDMARK_{i}"
        keypoints.append(Keypoint(
            name=name,
            x=lm.x,
            y=lm.y,
            z=lm.z,
            visibility=getattr(lm, "visibility", None),
        ))
    return keypoints
