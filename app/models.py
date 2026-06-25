from sqlalchemy import Column, Integer, String, DateTime
from database import Base  # Changed from 'app.database' to 'database'
from datetime import datetime

class Lead(Base):
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), default="")
    email = Column(String(100), default="")
    company = Column(String(100), default="")
    created_at = Column(DateTime, default=datetime.utcnow)