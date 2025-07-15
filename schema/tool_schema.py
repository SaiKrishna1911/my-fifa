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
]
