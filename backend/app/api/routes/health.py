from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database.database import engine, get_db


router = APIRouter()

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        database_status = "connected"
    except Exception:
        database_status = "disconnected"

    return {
        "status": "healthy" if database_status == "connected" else "unhealthy",
        "database": database_status,
        "crawler": "available",
    }
