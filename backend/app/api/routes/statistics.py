from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.services import statistics_service

router = APIRouter()


@router.get("/statistics/summary")
def get_summary(db: Session = Depends(get_db)):
    return statistics_service.get_summary(db)