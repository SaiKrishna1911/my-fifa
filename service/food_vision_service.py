import base64
from typing import Optional
from openai import OpenAI
from PIL import Image
from io import BytesIO

sync_client = OpenAI()  # Assumes OPENAI_API_KEY is in env

def estimate_nutrition_from_image(image_bytes: Optional[bytes] = None, image_b64: Optional[str] = None, goal: Optional[str] = None, db=None, user_id=None, confirm=False, date=None, **kwargs):
    print("Estimate nutrition")
    if image_bytes is not None:
        image_base64 = base64.b64encode(image_bytes).decode()
    elif image_b64 is not None:
        image_base64 = image_b64
    else:
        raise ValueError("Must provide either image_bytes or image_b64")

    goal_text = f"The user's goal is: {goal}" if goal else ""
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
{goal_text}
    """.strip()

    response = sync_client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "You are a meal recognition expert. Respond only in JSON with the following top-level structure:\n{\n  \"estimated_nutrition_facts\": {\n    \"calories\": \"<string, e.g. 600–750 kcal>\",\n    \"protein\": \"<string, e.g. 25–35g>\",\n    \"carbohydrates\": \"<string, e.g. 80–90g>\",\n    \"fats\": \"<string, e.g. 20–28g>\",\n    \"fiber\": \"<string, e.g. 2–4g>\",\n    ...\n  },\n  \"summary\": \"<string>\",\n  \"decent_quantity_recommendation\": [\"<string>\", ...],\n  \"fitness_goal_tip\": [\"<string>\", ...],\n  \"cooking_suggestion\": [\"<string>\", ...],\n  \"fun_message\": \"<string>\"\n}"},
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
    print("[DEBUG] Raw GPT Response:", result)
    if not result:
        raise ValueError("GPT returned empty response")

    # Optionally log to daily_plan_tracking if confirm is True
    if confirm and db and user_id:
        import json as _json
        from service.daily_plan_tracking_service import DailyPlanTrackingService
        from datetime import date as dt_date
        try:
            parsed = _json.loads(result) if isinstance(result, str) else result
            summary = parsed.get("text") or str(parsed)
            est = parsed.get("estimated_nutrition_facts") or {}
            if not est:
                print("[WARN] No 'estimated_nutrition_facts' in GPT response.")
            nutrition_estimates = est
            # Extract numerical nutrition values (robust parsing)
            def parse_float(val):
                import re
                if isinstance(val, (int, float)):
                    return float(val)
                if not isinstance(val, str):
                    return 0.0
                # Normalize common symbols
                val = val.replace("–", "-").replace("−", "-").replace(",", ".")
                nums = re.findall(r"\d+(?:\.\d+)?", val)  # Matches only real float numbers
                if not nums:
                    return 0.0
                try:
                    nums = [float(n) for n in nums]
                    return sum(nums) / len(nums)
                except Exception as e:
                    print("[WARN] parse_float fallback due to error:", e)
                    return 0.0

            calories = parse_float(nutrition_estimates.get("calories"))
            protein = parse_float(nutrition_estimates.get("protein"))
            carbohydrates = parse_float(nutrition_estimates.get("carbohydrates"))
            fat = parse_float(nutrition_estimates.get("fats") or nutrition_estimates.get("fat"))
            fiber = parse_float(nutrition_estimates.get("fiber"))
            log_date = date or dt_date.today().isoformat()
            print("nutrition_estimates before log_food_event:", nutrition_estimates)
            print("event", str(user_id), str(log_date), str(summary), str(calories), str(protein), str(carbohydrates), str(fat), str(fiber))
            DailyPlanTrackingService.log_food_event(
                db, user_id, log_date, summary, parse_float(calories),
                protein=protein, carbohydrates=carbohydrates, fat=fat, fiber=fiber
            )
            print(f"[DEBUG] Food event logged from food_vision_service for user_id={user_id}, date={log_date}")
        except Exception as e:
            print(f"[ERROR] Exception in food_vision_service logging: {e}")
    import json
    return json.loads(result)