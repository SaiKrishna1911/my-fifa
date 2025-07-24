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
},
{
    "type": "function",
    "function": {
        "name": "estimate_nutrition_from_image",
        "description": "Estimate nutrition facts from a food image. Use when the user uploads a food image or asks for nutrition analysis of a food photo.",
        "parameters": {
            "type": "object",
            "properties": {
                "image_b64": {
                    "type": "string",
                    "description": "Base64-encoded string of the uploaded food image."
                },
                "goal": {
                    "type": ["string", "null"],
                    "description": "User's fitness goal, if specified."
                },
                "user_id": {
                    "type": ["integer", "null"],
                    "description": "User ID for logging."
                }
            },
            "required": ["image_b64"]
        }
    }
},
{
    "type": "function",
    "function": {
        "name": "log_food_consumption",
        "description": "Log a food consumption event to the user's daily plan tracking after user confirms they ate the food. Use after nutrition estimate is shown and user says yes.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {"type": "integer", "description": "User ID for logging."},
                "date": {"type": "string", "description": "Date of consumption in YYYY-MM-DD format."},
                "summary": {"type": "string", "description": "Summary of the food consumed."},
                "calories": {"type": ["number", "null"], "description": "Estimated calories consumed."},
                "nutrition_estimates": {"type": ["object", "null"], "description": "Full nutrition estimates as a dict, if available."}
            },
            "required": ["user_id", "date", "summary"]
        }
    }
},
{
    "type": "function",
    "function": {
        "name": "log_exercise_event",
        "description": "Log an exercise event to the user's daily plan tracking. Use when the user completes an exercise and confirms it.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "integer",
                    "description": "User ID for logging."
                },
                "date": {
                    "type": "string",
                    "description": "Date of the exercise in YYYY-MM-DD format."
                },
                "summary": {
                    "type": "string",
                    "description": "Summary of the exercise performed."
                },
                "calories_burned": {
                    "type": ["number", "null"],
                    "description": "Estimated calories burned during the workout."
                },
                "reps_done": {
                    "type": ["integer", "null"],
                    "description": "Number of repetitions done, if applicable."
                },
                "form_score": {
                    "type": ["number", "null"],
                    "description": "Score indicating form quality, e.g., from posture validation."
                }
            },
            "required": ["user_id", "date", "summary"]
        }
    }
}
]
