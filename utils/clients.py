import os

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

sync_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))