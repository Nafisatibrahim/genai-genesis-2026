"""
Guided exercises: id, name, and text instructions (no demo video).
Used by GET /exercises and by posture feedback (exercise_id).
"""

EXERCISES = [
    {
        "id": "bodyweight_squat",
        "name": "Bodyweight squat",
        "instructions": (
            "Stand with feet shoulder-width apart. Push your hips back and bend your knees "
            "as if sitting into a chair. Keep your chest up and knees over your toes. "
            "Go as low as is comfortable, then stand back up."
        ),
    },
    {
        "id": "cat_cow",
        "name": "Cat–cow",
        "instructions": (
            "Start on hands and knees (tabletop), hands under shoulders, knees under hips. "
            "Cow: drop your belly, lift your chest and tailbone, look slightly up. "
            "Cat: round your spine toward the ceiling, tuck your tailbone, drop your head. "
            "Move slowly between the two for 5–10 breaths."
        ),
    },
    {
        "id": "chin_tucks",
        "name": "Chin tucks",
        "instructions": (
            "Sit or stand with your spine tall. Keep your eyes forward and pull your chin "
            "straight back (like making a double chin). Hold 2–3 seconds, then relax. "
            "Repeat 8–10 times. Do not tilt your head up or down—the motion is straight back."
        ),
    },
]


def get_exercises():
    """Return list of exercises for API (id, name, instructions)."""
    return list(EXERCISES)


def get_exercise(exercise_id: str):
    """Return one exercise by id, or None."""
    for ex in EXERCISES:
        if ex["id"] == exercise_id:
            return ex
    return None
