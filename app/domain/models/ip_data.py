from datetime import UTC, datetime
from typing import Optional

from pydantic import BaseModel, Field


class IpGeolocationData(BaseModel):
    """Domain entity representing geolocation data for an IP address or URL."""

    ip: str
    url: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    city: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    continent: Optional[str] = None
    postal_code: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    def update_location(
        self,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        city: Optional[str] = None,
        region: Optional[str] = None,
        country: Optional[str] = None,
        continent: Optional[str] = None,
        postal_code: Optional[str] = None,
    ):
        """Update the geolocation data fields and set updated timestamp."""
        if latitude is not None:
            self.latitude = latitude
        if longitude is not None:
            self.longitude = longitude
        if city is not None:
            self.city = city
        if region is not None:
            self.region = region
        if country is not None:
            self.country = country
        if continent is not None:
            self.continent = continent
        if postal_code is not None:
            self.postal_code = postal_code

        self.updated_at = datetime.now(UTC)

# json schema for the IpGeolocationData class
GeolocationData = IpGeolocationData.model_json_schema()
