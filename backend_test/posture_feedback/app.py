"""
Standalone FastAPI app for posture feedback (Phase 5.2–5.4).
POST /exercise-feedback: exercise_id + keypoints (or image_base64) -> corrections + safety_tips.
Run from repo root: python -m uvicorn backend_test.posture_feedback.app:app --reload --port 8001
Or from this folder: uvicorn app:app --reload --port 8001
"""

import asyncio
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Import from same package (run as module or from folder)
try:
    from .schemas import ExerciseFeedbackRequest, ExerciseFeedbackResponse, Keypoint
    from .gemini_feedback import get_exercise_feedback
    from . import pose as pose_module
except ImportError:
    from schemas import ExerciseFeedbackRequest, ExerciseFeedbackResponse, Keypoint
    from gemini_feedback import get_exercise_feedback
    import pose as pose_module

app = FastAPI(
    title="FlexCare Posture Feedback (test)",
    description="Exercise form feedback: send exercise_id + keypoints (or image), get corrections and safety tips from Gemini.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


class ExerciseFeedbackFromImageRequest(BaseModel):
    """Alternative: send a single frame as base64; server runs pose then Gemini."""
    exercise_id: str = Field(..., description="e.g. cat_cow, chin_tucks")
    exercise_name: str | None = None
    image_base64: str = Field(..., description="Base64-encoded image (JPEG/PNG) of the user doing the exercise")


@app.post("/exercise-feedback", response_model=ExerciseFeedbackResponse)
async def exercise_feedback(payload: ExerciseFeedbackRequest):
    """
    Request form feedback from Gemini given exercise_id and pose keypoints.
    Keypoints should be normalized 0-1 (e.g. from MediaPipe in the browser).
    """
    try:
        result = await asyncio.to_thread(get_exercise_feedback, payload)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/exercise-feedback-from-image", response_model=ExerciseFeedbackResponse)
async def exercise_feedback_from_image(payload: ExerciseFeedbackFromImageRequest):
    """
    Alternative: send a single image; server runs MediaPipe Pose to get keypoints,
    then Gemini for corrections and safety tips. Requires mediapipe + pillow.
    """
    try:
        keypoints = pose_module.image_base64_to_keypoints(payload.image_base64)
    except ImportError as e:
        raise HTTPException(status_code=503, detail=f"Pose from image not available: {e}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    request = ExerciseFeedbackRequest(
        exercise_id=payload.exercise_id,
        exercise_name=payload.exercise_name,
        keypoints=keypoints,
    )
    try:
        result = await asyncio.to_thread(get_exercise_feedback, request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
