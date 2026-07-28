from fastapi import FastAPI, APIRouter

router = APIRouter()

@router.get("/health")
def health_check():
    return {
  "status": "healthy",
  "databasgite": "connected",
  "crawler": "available"
}
