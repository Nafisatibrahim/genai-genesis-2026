"""
Pydantic schemas for posture feedback API.
Request: exercise_id + keypoints (from pose estimation).
Response: corrections + safety_tips from Gemini.
"""

from pydantic import BaseModel, Field


class Keypoint(BaseModel):
    """Single pose keypoint (e.g. MediaPipe landmark)."""
    name: str = Field(..., description="Landmark name, e.g. LEFT_SHOULDER, NOSE")
    x: float = Field(..., ge=0, le=1, description="Normalized x (0-1)")
    y: float = Field(..., ge=0, le=1, description="Normalized y (0-1)")
    z: float | None = Field(None, description="Normalized z (depth)")
    visibility: float | None = Field(None, ge=0, le=1, description="Visibility score")


class ExerciseFeedbackRequest(BaseModel):
    """Input: which exercise + pose keypoints (one frame or representative)."""
    exercise_id: str = Field(..., description="e.g. cat_cow, chin_tucks, child_pose")
    exercise_name: str | None = Field(None, description="Human-readable name for Gemini")
    keypoints: list[Keypoint] = Field(..., min_length=1, description="Pose keypoints from MediaPipe or similar")


class ExerciseFeedbackResponse(BaseModel):
    """Output: form corrections and safety tips from Gemini."""
    corrections: list[str] = Field(default_factory=list, description="1-2 short form corrections")
    safety_tips: list[str] = Field(default_factory=list, description="1-2 tips to avoid further injury")
