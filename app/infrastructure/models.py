import uuid
from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, Float, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class BaseModel(Base):  # type: ignore[misc,valid-type]
    __abstract__ = True
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )


class IpGeolocation(BaseModel):
    __tablename__ = "ip_geolocation"
    ip = Column(String, unique=True)
    url = Column(String, nullable=True)
    latitude = Column(Float)
    longitude = Column(Float)
    city = Column(String)
    region = Column(String)
    country = Column(String)
    continent = Column(String)
    postal_code = Column(String)

    class Config:
        from_attributes = True
