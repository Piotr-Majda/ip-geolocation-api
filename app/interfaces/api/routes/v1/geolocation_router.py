import traceback
from typing import Annotated, Optional
from urllib.parse import urlparse

import tldextract
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import (
    AfterValidator,
    BaseModel,
    Field,
    IPvAnyAddress,
    WithJsonSchema,
    model_validator,
)

from app.application.geolocation_service import (
    GeolocationApplicationService,
    NotFoundGeolocationData,
)
from app.core.logging import api_logger
from app.domain.services import IpGeolocationServiceError
from app.infrastructure.database import DatabaseUnavailableError
from app.interfaces.api.routes.dependencies import get_geolocation_application_service

router = APIRouter(prefix="/geolocation", tags=["Geolocation"])


def domain_validator(value: str) -> str:
    if not isinstance(value, str):
        raise TypeError("Domain must be a string")
    # Extract domain if URL
    if value.startswith("http://") or value.startswith("https://"):
        parsed = urlparse(value)
        host = parsed.hostname
    else:
        host = value.split(":")[0]
    if not host:
        raise ValueError(f"Invalid domain: host is empty for {value}")
    ext = tldextract.extract(host)
    # ext.domain and ext.suffix must both be non-empty for a valid domain
    if not ext.domain or not ext.suffix:
        raise ValueError(f"Invalid domain: {host} is not a valid domain for {value}")
    registered_domain = f"{ext.domain}.{ext.suffix}"
    return registered_domain


DomainStr = Annotated[
    str,
    AfterValidator(domain_validator),
    WithJsonSchema(
        {
            "type": "string",
            "format": "domain",
            "examples": ["www.example.com"],
            "description": "A domain name (e.g., www.example.com) or "
            "a URL from which a domain can be extracted.",
        }
    ),
]


class GeolocationRequest(BaseModel):
    url: Optional[DomainStr] = Field(
        None,
        description="Please provide a valid domain name (e.g., www.example.com) or "
        "a URL from which a domain can be extracted.",
    )
    ip_address: Optional[IPvAnyAddress] = Field(
        None,
        description="IP address ipv4 or ipv6",
        examples=["127.0.0.1", "::1"],
    )

    @model_validator(mode="after")
    def validate_request(self):
        if self.ip_address is None and self.url is None:
            raise ValueError("Either ip_address or url must be provided")
        if self.ip_address is not None and self.url is not None:
            raise ValueError("Only one of ip_address or url must be provided")
        return self


@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_geolocation(
    request: GeolocationRequest,
    geolocation_application_service: Annotated[
        GeolocationApplicationService, Depends(get_geolocation_application_service)
    ],
):
    """
    Add or update geolocation data by IP address or URL.
    If the record exists, it will be updated with fresh data from the external service.

    Args:
        request (GeolocationRequest): IP address or URL to add/update geolocation
        geolocation_application_service
            (Annotated[GeolocationApplicationService, Depends]): Geolocation application service

    Raises:
        HTTPException: Internal server error
        HTTPException: External service error

    Returns:
        JsonResponse: Success response with geolocation data
    """
    try:
        if request.ip_address is not None:
            geolocation = await geolocation_application_service.add_ip_data(str(request.ip_address))
        else:
            geolocation = await geolocation_application_service.add_url_data(str(request.url))
        return {
            "status": "success",
            "data": {"geolocation": geolocation.model_dump()},
        }

    except DatabaseUnavailableError as e:
        api_logger.error(f"Database unavailable: \n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database unavailable"
        )
    except IpGeolocationServiceError as e:
        api_logger.error(f"External service unavailable: \n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="External unavailable"
        )
    except NotFoundGeolocationData as e:
        api_logger.error(f"IP data not found: \n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="IP data not found on external service"
        )
    except Exception as e:
        api_logger.error(f"Error adding/updating geolocation: \n{traceback.format_exc()}")
        raise e


@router.delete("/")
async def delete_geolocation(
    geolocation_application_service: Annotated[
        GeolocationApplicationService, Depends(get_geolocation_application_service)
    ],
    ip_address: Optional[IPvAnyAddress] = None,
    url: Optional[DomainStr] = None,
):
    """
    Delete geolocation by IP address or URL

    Args:
        ip_address: IP address to delete geolocation
        url: URL to delete geolocation
        geolocation_application_service
            (Annotated[GeolocationApplicationService, Depends]): Geolocation application service

    Raises:
        HTTPException: Internal server error
        HTTPException: External service error

    Returns:
        JsonResponse: Success response
    """
    if (ip_address is None and url is None) or (ip_address is not None and url is not None):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Provide either ip_address or url, not both.",
        )
    try:
        if ip_address is not None:
            result = await geolocation_application_service.delete_ip_data(str(ip_address))
        else:
            result = await geolocation_application_service.delete_url_data(str(url))
    except DatabaseUnavailableError as e:
        api_logger.error(f"Database unavailable: \n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database unavailable"
        )
    except Exception as e:
        api_logger.error(f"Error deleting geolocation: \n{traceback.format_exc()}")
        raise e
    if result:
        return {"status": "success", "data": {"ip_address": ip_address, "url": url}}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Geolocation data not found"
        )


@router.get("/")
async def get_geolocation(
    geolocation_application_service: Annotated[
        GeolocationApplicationService, Depends(get_geolocation_application_service)
    ],
    ip_address: Optional[IPvAnyAddress] = None,
    url: Optional[DomainStr] = None,
):
    """
    Get geolocation by IP address or URL not both

    Args:
        ip_address: IP address to get geolocation
        url: URL to get geolocation
        geolocation_application_service
            (Annotated[GeolocationApplicationService, Depends]): Geolocation application service

    Raises:
        HTTPException: Internal server error
        HTTPException: External service error

    Returns:
        JsonResponse: Success response
    """
    if (ip_address is None and url is None) or (ip_address is not None and url is not None):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Provide either ip_address or url, not both.",
        )
    try:
        if ip_address is not None:
            data = await geolocation_application_service.get_ip_data(str(ip_address))
        else:
            data = await geolocation_application_service.get_url_data(str(url))
    except DatabaseUnavailableError as e:
        api_logger.error(f"Database unavailable: \n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database unavailable"
        )
    except Exception as e:
        api_logger.error(f"Error getting geolocation: \n{traceback.format_exc()}")
        raise e
    if data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Geolocation data not found"
        )
    return {"status": "success", "data": {"geolocation": data.model_dump()}}
