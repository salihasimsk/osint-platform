from fastapi import FastAPI
from app.api.routes import health, sources,advisories,crawls,logs
from app.database.database import Base, engine
from app.models import source, advisory,crawl_job


Base.metadata.create_all(bind=engine) 

app = FastAPI(title="OSINT Web Crawler API")
app.include_router(health.router,prefix="/api")
app.include_router(sources.router,prefix="/api")
app.include_router(advisories.router,prefix="/api")
app.include_router(crawls.router, prefix="/api")
app.include_router(logs.router, prefix="/api") 

@app.get("/")
def root():
    return {"message": "OSINT Web Crawler API is running."}
