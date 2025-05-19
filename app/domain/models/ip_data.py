from datetime import datetime
from typing import Optional

from pydantic import AnyUrl, BaseModel, Field, IPvAnyAddress


class Geolocation(BaseModel):

    ip: Optional[IPvAnyAddress] = Field(None, description="IP address")
    url: Optional[AnyUrl] = Field(None, description="URL")
    latitude: float = Field(..., description="Latitude")
    longitude: float = Field(..., description="Longitude")
    city: str = Field(..., description="City")
    region: str = Field(..., description="Region")
    country: str = Field(..., description="Country")
    continent: str = Field(..., description="Continent")
    postal_code: str = Field(..., description="Postal code")
    created_at: Optional[datetime] = Field(None, description="Created at timestamp")
    updated_at: Optional[datetime] = Field(None, description="Updated at timestamp")
