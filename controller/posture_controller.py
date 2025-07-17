from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from service.posture_validator import validate_posture
import base64

router = APIRouter()

@router.post("/posture/validate")
async def validate_posture_api(
    video_file: UploadFile = File(...),
    exercise: str = Form(...)
):
    if not (video_file.content_type.startswith("video/") or video_file.content_type == "image/gif"):
        raise HTTPException(status_code=400, detail="Only video or GIF files are accepted.")

    video_bytes = await video_file.read()
    video_b64 = base64.b64encode(video_bytes).decode("utf-8")

    result = validate_posture(exercise=exercise, video_b64=video_b64)
    return result