"""
Quick test: POST sample keypoints to local posture-feedback API.
Run the app first: uvicorn backend_test.posture_feedback.app:app --port 8001
Then: python backend_test/posture_feedback/test_request.py
"""

import json
import urllib.request
import sys

URL = "http://localhost:8001/exercise-feedback"

# Minimal keypoints (normalized 0-1) simulating a standing pose
SAMPLE_KEYPOINTS = [
    {"name": "NOSE", "x": 0.5, "y": 0.15},
    {"name": "LEFT_SHOULDER", "x": 0.35, "y": 0.25},
    {"name": "RIGHT_SHOULDER", "x": 0.65, "y": 0.25},
    {"name": "LEFT_ELBOW", "x": 0.25, "y": 0.45},
    {"name": "RIGHT_ELBOW", "x": 0.75, "y": 0.45},
    {"name": "LEFT_HIP", "x": 0.4, "y": 0.6},
    {"name": "RIGHT_HIP", "x": 0.6, "y": 0.6},
    {"name": "LEFT_KNEE", "x": 0.38, "y": 0.8},
    {"name": "RIGHT_KNEE", "x": 0.62, "y": 0.8},
    {"name": "LEFT_ANKLE", "x": 0.37, "y": 0.95},
    {"name": "RIGHT_ANKLE", "x": 0.63, "y": 0.95},
]

payload = {
    "exercise_id": "cat_cow",
    "exercise_name": "Cat-cow stretch",
    "keypoints": SAMPLE_KEYPOINTS,
}

def main():
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(URL, data=data, method="POST", headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            out = json.load(res)
            print(json.dumps(out, indent=2))
    except urllib.error.HTTPError as e:
        print(e.read().decode(), file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Error: {e}. Is the app running on port 8001?", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
