from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.database.database import Base


class CrawlLog(Base):
    __tablename__ = "crawl_logs"

    id = Column(Integer, primary_key=True, index=True)
    crawl_job_id = Column(String, index=True, nullable=True)
    log_level = Column(String, default="info", index=True)
    message = Column(Text, nullable=False)
    source = Column(String, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())