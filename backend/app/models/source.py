from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database.database import Base

class Source(Base):
    
    __tablename__ = "sources"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String,nullable=False)
    base_url = Column(String,nullable=False)
    enabled_status = Column(Boolean,default=True)
    request_delay = Column(Integer,default=2)
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    updated_date = Column(DateTime(timezone=True), onupdate=func.now())
    last_crawl_date = Column(DateTime(timezone=True), nullable=True)
    