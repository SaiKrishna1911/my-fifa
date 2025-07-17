from typing import List, Dict

from dotenv import load_dotenv
from fastapi import FastAPI

from constants.system_promt import SYSTEM_PROMPT
from controller.chat_controller import router as chat_router
from controller.user_controller import router as user_router
from utils.utils import is_exit_message, run_with_tools
from controller.plan_controller import router as plan_router
from controller.food_controller import router as food_router
from controller.posture_controller import router as posture_router

load_dotenv()

app = FastAPI(title="AI Gym Coach")
app.include_router(chat_router)
app.include_router(user_router)
app.include_router(plan_router)
app.include_router(food_router)
app.include_router(posture_router)


@app.get("/")
def root():
    return {"status": "ok"}

if __name__ == "__main__":
    chat_history: List[Dict[str, str]] = []
    print("🏋️  AI Gym Coach — type 'exit' to quit.")
    while True:
        user = input("\nYou: ").strip()
        result = is_exit_message(user)
        if result.lower() != "continue":
            print(f"{result}")
            break
        chat_history.append({"role": "user", "content": user})
        reply = run_with_tools([{"role": "system", "content": SYSTEM_PROMPT}] + chat_history).content.strip()
        chat_history.append({"role": "assistant", "content": reply})
        print("Coach:", reply)