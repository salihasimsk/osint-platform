from fastapi import FastAPI
from app.api.routes import health, sources,advisories,crawls,logs,statistics
from app.database.database import Base, engine
from app.models import source, advisory,crawl_job
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI(title="OSINT Web Crawler API")

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router,prefix="/api")
app.include_router(sources.router,prefix="/api")
app.include_router(advisories.router,prefix="/api")
app.include_router(crawls.router, prefix="/api")
app.include_router(logs.router, prefix="/api")
app.include_router(statistics.router, prefix="/api")

@app.get("/")
def root():
    return {"message": "OSINT Web Crawler API is running."}
