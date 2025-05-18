from typing import AsyncGenerator
from fastapi import Depends

from app.infrastructure.database import DatabaseClient
from app.application.geolocation_service import GeolocationApplicationService
from app.domain.repositories import IpGeolocationRepository
from app.domain.services import IpGeolocationService
from app.core.config import settings
from app.infrastructure.ipstack_geolocation_service import IpStackGeolocationService
from app.infrastructure.ip_geolocation_repository import IpGeolocationRepositoryImpl


async def get_database_client() -> AsyncGenerator[DatabaseClient, None]:
    db = DatabaseClient(url=settings.DATABASE_URL)
    db.connect()
    try:
        yield db
    finally:
        await db.close()


def get_ip_geolocation_repository(database_client: DatabaseClient = Depends(get_database_client)) -> IpGeolocationRepository:
    return IpGeolocationRepositoryImpl(database_client=database_client)


def get_ip_geolocation_service() -> IpGeolocationService:
    return IpStackGeolocationService(api_key=settings.IPSTACK_API_KEY)


def get_geolocation_application_service(
    ip_geolocation_repository: IpGeolocationRepository = Depends(get_ip_geolocation_repository), 
    ip_geolocation_service: IpGeolocationService = Depends(get_ip_geolocation_service)
    ) -> GeolocationApplicationService:
    return GeolocationApplicationService(
        repository=ip_geolocation_repository,
        external_service=ip_geolocation_service
    )
