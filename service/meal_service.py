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
    print("Suggest Meals")
    prompt = f"""
You're a fitness-focused meal planner. Suggest 2-3 **high-protein meals** tailored for someone with the following profile:

🍱 Meal Requests:
- If the user asks about meals, food, diet, nutrition, recovery food, etc., call the `suggest_meals` tool.
- If he asking for analysis over an image, call estimate_nutrition_from_image this method.
- Infer total calories and protein based on user messages (e.g. age, gender, weight, fitness goal). If not enough info, use general healthy defaults (e.g. 2200 kcal, 120g protein) and let the user know.

📉 If you don’t have enough info:
Say something fun but clear:
“Hmm, I’m missing a few reps of info here. Gimme a bit more context and I’ll coach you right through it!”


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
