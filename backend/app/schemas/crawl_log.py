from pydantic import BaseModel, ConfigDict
from datetime import datetime


class CrawlLogResponse(BaseModel):
    id: int
    crawl_job_id: int | None = None
    log_level: str
    message: str
    source: str | None = None
    timestamp: datetime | None = None

    model_config = ConfigDict(from_attributes=True)