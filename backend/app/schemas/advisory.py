from pydantic import BaseModel,ConfigDict
from datetime import datetime

class AdvisoryBase(BaseModel):
    title: str 
    organization: str
    publication_date: datetime | None = None
    url: str
    source_domain: str
    cve: str | None = None
    product: str | None = None
    severity: str | None = None
    summary: str | None = None
    craw_job_id: int | None = None
    

class AdvisoryCreate(AdvisoryBase):
    pass

class AdvisoryResponse(AdvisoryBase):
    id: int
    collection_date: datetime

    model_config = ConfigDict(from_attributes=True)