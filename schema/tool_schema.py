TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "find_exercise",
            "description": "Return a YouTube link for an exercise.",
            "parameters": {
                "type": "object",
                "properties": {
                    "body_part": {"type": ["string", "null"]},
                    "exercise_name": {"type": ["string", "null"]},
                    "equipment": {"type": ["string", "null"]},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "suggest_meals",
            "description": (
                "Suggest high-protein meals tailored to the user’s goal (e.g. fat loss, muscle gain), "
                "age, weight, gender, and allergies. Use average macros if not provided."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "goal": {"type": "string"},
                    "age": {"type": ["integer", "null"]},
                    "weight_kg": {"type": ["number", "null"]},
                    "gender": {"type": ["string", "null"]},
                    "allergies": {
                        "type": ["array", "null"],
                        "items": {"type": "string"}
                    },
                },
                "required": ["goal"]
            },
        },
    },
{
    "type": "function",
    "function": {
        "name": "validate_posture",
        "description": (
            "Analyze the user's exercise form from an uploaded video. "
            "Use this tool when the user asks to check their posture, form, or exercise correctness."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "exercise": {
                    "type": "string",
                    "description": "The name of the exercise being performed (e.g., 'push-up', 'squat')."
                },
                "video_b64": {
                    "type": "string",
                    "description": "Base64-encoded string of the uploaded video clip."
                },
                "engine": {
                    "type": "string",
                    "enum": ["mediapipe", "yolov8"],
                    "default": "mediapipe",
                    "description": "Which backend engine to use for posture validation."
                }
            },
            "required": ["exercise", "video_b64"]
        }
    }
}
]
