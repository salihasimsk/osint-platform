from pydantic import BaseModel,ConfigDict
from datetime import datetime

class SourceBase(BaseModel):
    name: str
    base_url: str
    enabled_status: bool = True
    request_delay: int = 2
    
class SourceCreate(SourceBase):
    pass

class SourceResponse(SourceBase):
    id: int
    created_date: datetime
    updated_date: datetime | None = None
    last_crawl_date: datetime | None = None

    model_config = ConfigDict(from_attributes=True)