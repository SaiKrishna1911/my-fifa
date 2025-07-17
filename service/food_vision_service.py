import base64
from typing import Optional
from openai import OpenAI
from PIL import Image
from io import BytesIO

sync_client = OpenAI()  # Assumes OPENAI_API_KEY is in env

def estimate_nutrition_from_image(image_bytes: bytes, goal: Optional[str] = None):
    print("Estimate nutrition")
    image_base64 = base64.b64encode(image_bytes).decode()

    prompt = f"""
You're a fitness-focused nutritionist. Estimate nutrition facts from a food image.
Mention the decent quantity to be consumed for a normal person, and if goal is specified mention that as well. 
Don't say food is Junk food even if it is. Say it has more than normal contents of nutriention facts which is not suitable to hit the goals, but can be taken if
the craving is high. 

🍱 Meal Requests:
- If the user asks about meals, food, diet, nutrition, recovery food, etc., call the `suggest_meals` tool.
- If he asking for analysis over an image, call estimate_nutrition_from_image this method.
- Infer total calories and protein based on user messages (e.g. age, gender, weight, fitness goal). If not enough info, use general healthy defaults (e.g. 2200 kcal, 120g protein) and let the user know.

📉 If you don’t have enough info:
Say something fun but clear:
“Hmm, I’m missing a few reps of info here. Gimme a bit more context and I’ll coach you right through it!”


Follow up with a cooking suggestion. 
Return a structured JSON response in bullet points, don't be soo sure on facts, have an approximations if not sure.
{f"The user's goal is: {goal}" if goal else ""}
    """.strip()

    response = sync_client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "You are a meal recognition expert. Return JSON Response Only"},
            {"role": "user", "content": prompt},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        },
                    }
                ],
            },
        ]
    )

    result = response.choices[0].message.content.strip()
    return result