# dependencies.py
from sqlalchemy.orm import Session
from schema.database import SessionLocal  # or however you setup your DB

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()