from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from schema.dependencies import get_db
from entity.users import User, UserResponse

router = APIRouter()


class UserCreateUpdate(BaseModel):
    name: str
    age: int
    height_cm: float
    weight_kg: float
    status: str
    allergies: List[str] = []
    goal: Optional[str] = None


@router.post("/users", response_model=UserResponse)
def create_user(user_data: UserCreateUpdate, db: Session = Depends(get_db)):
    user = User(**user_data.dict())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_data: UserCreateUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    for key, value in user_data.dict().items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user