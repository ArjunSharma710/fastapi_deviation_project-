from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from .database import Base


class Deviation(Base):
    __tablename__ = "deviations"

    id = Column(Integer, primary_key=True, index=True)
    site = Column(String, nullable=False)
    batch_number = Column(String, nullable=False)
    event_datetime = Column(DateTime, nullable=True)
    description = Column(Text, nullable=False)
    category = Column(String, nullable=True)
    impact = Column(String, nullable=True)
    severity = Column(String, nullable=True)
    severity_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)