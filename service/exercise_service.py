import os
from http.client import HTTPException
from typing import Optional, Dict, Any

from fastapi import requests

from constants.body_parts import BODY_PART_MAP

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.youtube.com/watch?v={vid}"


def find_exercise(body_part: Optional[str] = None, exercise_name: Optional[str] = None, equipment: Optional[str] = None) -> Dict[str, Any]:
    print("Find Exercise")
    if exercise_name:
        query = exercise_name
    elif body_part:
        query = f"{BODY_PART_MAP.get(body_part.lower(), body_part)} workout exercise gym"
    else:
        raise HTTPException(400, "Provide either body_part or exercise_name")

    clip = fetch_youtube_clip(query)
    if not clip:
        raise HTTPException(404, f"No YouTube video found for: {query}")

    return {
        "name": exercise_name or f"{body_part.title()} Exercise",
        "video_url": clip,
        "primary_muscles": [body_part.lower()] if body_part else [],
        "equipment": equipment or "body weight",
    }

def fetch_youtube_clip(query: str) -> Optional[str]:
    if not YOUTUBE_API_KEY:
        return None
    params = {
        "part": "snippet", "q": query, "type": "video", "videoDuration": "short",
        "key": YOUTUBE_API_KEY, "maxResults": 3, "safeSearch": "strict"
    }
    r = requests.get(YOUTUBE_SEARCH_URL, params=params, timeout=15)
    if r.status_code != 200:
        return None
    for item in r.json().get("items", []):
        vid = item["id"].get("videoId")
        title = item["snippet"]["title"].lower()
        if vid and not any(bad in title for bad in ("funny", "fail", "meme")):
            return YOUTUBE_VIDEO_URL.format(vid=vid)
    return None

