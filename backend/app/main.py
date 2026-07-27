from fastapi import FastAPI
from app.api.routes import health

app = FastAPI(title="OSINT Web Crawler API")
app.include_router(health.router,prefix="/api")

@app.get("/")
def root():
    return {"message": "OSINT Web Crawler API is running."}
