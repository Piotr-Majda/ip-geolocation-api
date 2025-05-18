
from datetime import datetime, UTC
import uuid
from sqlalchemy import Column, Integer, DateTime, String, Float
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC))

class IpGeolocation(BaseModel):
    __tablename__ = "ip_geolocation"
    ip = Column(String, primary_key=True)
    url = Column(String, nullable=True)
    latitude = Column(Float)
    longitude = Column(Float)
    city = Column(String)
    region = Column(String)
    country = Column(String)
    continent = Column(String)
    postal_code = Column(String)
    timezone = Column(String)
    isp = Column(String)
    
    class Config:
        from_attributes = True
