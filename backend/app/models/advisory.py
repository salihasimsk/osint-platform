from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.database.database import Base

class Advisory(Base):

    __tablename__ = "advisories"
    id = Column(Integer, primary_key = True, index= True)
    title = Column(String,nullable=False)
    organization = Column(String,nullable=False)
    publication_date = Column(DateTime(timezone=True))
    url = Column(String,nullable=False)
    source_domain = Column(String, nullable=False)
    cve = Column(String,nullable=True, index=True)
    product = Column(String, nullable=True)
    severity = Column(String, nullable=True, index=True)
    summmary = Column(Text, nullable=True)
    collection_date = Column(DateTime(timezone=True), server_default=func.now())
    crawl_job_id = Column(Integer, nullable=True, index=True)
    
    