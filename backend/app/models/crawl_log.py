from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base


class CrawlLog(Base):
    __tablename__ = "crawl_logs"

    id = Column(Integer, primary_key=True, index=True)
    log_level = Column(String, default="info", index=True)
    message = Column(Text, nullable=False)
    source = Column(String, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    crawl_job_id = Column(Integer, ForeignKey("crawl_jobs.id"), index=True, nullable=True)
    crawl_job = relationship("CrawlJob", back_populates="crawl_logs")
