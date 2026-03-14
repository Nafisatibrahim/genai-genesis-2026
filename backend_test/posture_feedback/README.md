# Posture feedback (standalone test)

**How does Gemini know which posture the person is doing?**  
This folder implements the flow separately before integrating into the main app.

## Flow

1. **Identify the exercise** — Client sends `exercise_id` (e.g. `cat_cow`) and optional `exercise_name` (e.g. "Cat-cow stretch").
2. **Get pose** — Either:
   - **Client sends keypoints** (from MediaPipe in the browser): `POST /exercise-feedback` with `{ "exercise_id", "keypoints": [{ "name", "x", "y", "z?", "visibility?" }] }`.
   - **Client sends image** (single frame): `POST /exercise-feedback-from-image` with `{ "exercise_id", "image_base64" }`; server runs MediaPipe Pose to get keypoints.
3. **Backend / Gemini** — Keypoints + exercise name are sent to Gemini with a prompt; response is parsed into `corrections` and `safety_tips`.

## Endpoints

| Method | Path | Body | Description |
|--------|------|------|-------------|
| GET | `/health` | — | Readiness check. |
| POST | `/exercise-feedback` | `ExerciseFeedbackRequest` | Form feedback from **keypoints** (client does pose). |
| POST | `/exercise-feedback-from-image` | `exercise_id`, `image_base64` | Form feedback from **image** (server does pose). |

## Request/response

**POST /exercise-feedback**

```json
{
  "exercise_id": "cat_cow",
  "exercise_name": "Cat-cow stretch",
  "keypoints": [
    { "name": "LEFT_SHOULDER", "x": 0.3, "y": 0.2 },
    { "name": "RIGHT_SHOULDER", "x": 0.7, "y": 0.2 },
    { "name": "LEFT_HIP", "x": 0.35, "y": 0.6 },
    { "name": "RIGHT_HIP", "x": 0.65, "y": 0.6 }
  ]
}
```

**Response**

```json
{
  "corrections": ["Keep your back straighter in the cow position.", "..."],
  "safety_tips": ["Avoid rounding your lower back sharply.", "Stop if you feel sharp pain."]
}
```

Keypoints use normalized coordinates (0–1). Names should match MediaPipe Pose landmarks (e.g. `LEFT_SHOULDER`, `RIGHT_HIP`, `NOSE`).

## Setup

From repo root or from this folder:

```bash
cd backend_test/posture_feedback
pip install -r requirements.txt
```

Set `GEMINI_API_KEY` in `.env` (in repo root or this folder).

## Run

**From repo root (as module):**

```bash
uvicorn backend_test.posture_feedback.app:app --reload --port 8001
```

**From this folder:**

```bash
cd backend_test/posture_feedback
uvicorn app:app --reload --port 8001
```

Then:

- `GET http://localhost:8001/health`
- `POST http://localhost:8001/exercise-feedback` with JSON body as above.

## Integration later

When wiring into the main app:

- Main backend can add `POST /exercise-feedback` that delegates to this logic (or include this module).
- Frontend: after capturing frames in ExerciseCapture, run MediaPipe in the browser to get keypoints, then POST keypoints + `exercise_id` to the API.
