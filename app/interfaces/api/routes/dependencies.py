from typing import AsyncGenerator

from fastapi import Depends, HTTPException, status

from app.application.geolocation_service import GeolocationApplicationService
from app.core.config import settings
from app.domain.repositories import IpGeolocationRepository
from app.domain.services import IpGeolocationService
from app.infrastructure.database import DatabaseClient, DatabaseUnavailableError
from app.infrastructure.ip_geolocation_repository import IpGeolocationRepositoryImpl
from app.infrastructure.ipstack_geolocation_service import IpStackGeolocationService


async def get_database_client() -> AsyncGenerator[DatabaseClient, None]:
    db = DatabaseClient(url=settings.DATABASE_URL)
    try:
        db.connect()
        yield db
    except DatabaseUnavailableError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)) from e
    finally:
        await db.close()


def get_ip_geolocation_repository(
    database_client: DatabaseClient = Depends(get_database_client),
) -> IpGeolocationRepository:
    return IpGeolocationRepositoryImpl(database_client=database_client)


def get_ip_geolocation_service() -> IpGeolocationService:
    return IpStackGeolocationService(api_key=settings.IPSTACK_API_KEY)


def get_geolocation_application_service(
    ip_geolocation_repository: IpGeolocationRepository = Depends(get_ip_geolocation_repository),
    ip_geolocation_service: IpGeolocationService = Depends(get_ip_geolocation_service),
) -> GeolocationApplicationService:
    return GeolocationApplicationService(
        repository=ip_geolocation_repository, external_service=ip_geolocation_service
    )
