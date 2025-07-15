import json
from http.client import HTTPException
from typing import Optional, List

from utils.clients import sync_client


def suggest_meals(
        goal: str,
        age: Optional[int] = None,
        weight_kg: Optional[float] = None,
        gender: Optional[str] = None,
        allergies: Optional[List[str]] = None
):
    prompt = f"""
You're a fitness-focused meal planner. Suggest 2-3 **high-protein meals** tailored for someone with the following profile:

Goal: {goal}
Age: {age or 'unknown'}
Weight: {weight_kg or 'unknown'} kg
Gender: {gender or 'unknown'}
Allergies: {', '.join(allergies) if allergies else 'None'}

Each meal should include:
- name
- ingredients (list)
- protein_g (int)
- calories (int)
- prep (short instruction)

Output MUST be **pure JSON**. Do not explain anything, just return a valid JSON array of meals.
"""

    resp = sync_client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "You are a fitness meal generator. Output JSON only."},
            {"role": "user", "content": prompt.strip()}
        ]
    )

    content = resp.choices[0].message.content.strip()
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        raise HTTPException(500, f"Invalid JSON returned from GPT: {content}")
