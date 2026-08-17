from sqlalchemy import Column, Integer,String, JSON, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database.database import Base
from sqlalchemy.orm import relationship

class CrawlJob(Base):
    __tablename__ ="crawl_jobs"
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String,unique=True, nullable=False, index=True)
    status = Column(String, default="queued", index=True)
    progress = Column(Integer, default=0)
    pages_visited = Column(Integer, default=0)
    records_extracted = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    configuration = Column(JSON, nullable=True)
    started_date = Column(DateTime(timezone=True), nullable=True)
    completed_date = Column(DateTime(timezone=True), nullable=True)

    advisories = relationship('Advisory', back_populates='crawl_job')
    crawl_logs = relationship('CrawlLog', back_populates='crawl_job', cascade="all, delete-orphan")

    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False, index=True)
    source = relationship('Source', back_populates='crawl_jobs')
