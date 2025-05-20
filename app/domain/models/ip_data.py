from datetime import datetime
from typing import Optional

from pydantic import AnyUrl, BaseModel, Field, IPvAnyAddress, field_validator, TypeAdapter


class Geolocation(BaseModel):

    ip: Optional[str] = Field(None, description="IP address")
    url: Optional[str] = Field(None, description="URL")
    latitude: float = Field(..., description="Latitude")
    longitude: float = Field(..., description="Longitude")
    city: str = Field(..., description="City")
    region: str = Field(..., description="Region")
    country: str = Field(..., description="Country")
    continent: str = Field(..., description="Continent")
    postal_code: str = Field(..., description="Postal code")
    created_at: Optional[datetime] = Field(None, description="Created at timestamp")
    updated_at: Optional[datetime] = Field(None, description="Updated at timestamp")

    @field_validator("ip", mode="before")
    def validate_ip(cls, v):
        if v is None:
            return None
        return str(TypeAdapter(IPvAnyAddress).validate_python(v))

    @field_validator("url", mode="before")
    def validate_url(cls, v):
        if v is None:
            return None
        return str(TypeAdapter(AnyUrl).validate_python(v))
