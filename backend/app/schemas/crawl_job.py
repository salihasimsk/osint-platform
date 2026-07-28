from pydantic import BaseModel, ConfigDict
from datetime import datetime,date

class CrawlJobCreate(BaseModel):
    source_ids : list[int]
    maximum_pages : int = 100
    date_from: date| None = None
    keywords: list[str]| None = None
    
class CrawlJobResponse(BaseModel):
    job_id: str
    status: str
    progress: int
    pages_visited: int
    records_extracted: int
    error_count: int
    started_date: datetime | None = None
    completed_date: datetime | None = None
    
    model_config = ConfigDict(from_attributes=True)
    