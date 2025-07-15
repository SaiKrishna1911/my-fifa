# 🏋️‍♂️ AI Gym Coach – FIFA

A FastAPI-based intelligent gym assistant that helps users with:

- 📚 Structured workouts
- 🍱 Meal suggestions
- 💬 Conversational fitness coaching
- 📸 Food image → nutrition estimation (experimental)

---

## 🚀 Features

- 💬 GPT-4.1-powered chat
- 🏃‍♂️ Suggest workouts by body part or goal
- 🍗 Generate meals based on calories & protein needs
- 🔐 User plans & subscriptions
- 📦 Modular architecture using FastAPI + SQLAlchemy + Pydantic

---

## 🛠️ Tech Stack

- FastAPI
- GPT-4.1 via OpenAI API
- SQLAlchemy
- MySQL
- Pydantic
- YouTube API (for video lookup)

---

## Future plans
- Voice chat capability
- Posture Validation

## 🧪 Running Locally

```bash
git clone https://github.com/YOUR_USERNAME/fifa-ai-coach.git
cd fifa-ai-coach
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
