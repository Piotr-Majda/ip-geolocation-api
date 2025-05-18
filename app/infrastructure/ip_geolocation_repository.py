import traceback
from typing import List, Optional

from sqlalchemy import delete, select
from sqlalchemy.exc import OperationalError

from app.core.logging import get_logger
from app.domain.models.ip_data import IpGeolocationData
from app.domain.repositories import IpGeolocationRepository
from app.infrastructure.database import DatabaseClient, DatabaseUnavailableError
from app.infrastructure.models import IpGeolocation

logger = get_logger(__name__)


class IpGeolocationRepositoryImpl(IpGeolocationRepository):

    def __init__(self, database_client: DatabaseClient):
        self.database_client = database_client

    async def add(self, ip_data: IpGeolocationData) -> IpGeolocationData:
        """
        Add new IP geolocation data to the repository.

        Args:
            ip_data: The geolocation data to add

        Returns:
            The added geolocation data with any generated fields
        """
        async with self.database_client.get_session() as session:
            db_obj = IpGeolocation(**ip_data.model_dump())
            session.add(db_obj)
            try:
                await session.commit()
                await session.refresh(db_obj)
            except OperationalError as e:
                await session.rollback()
                logger.error(f"Operational error adding: \n{e}")
                raise DatabaseUnavailableError(f"Database error") from e

            return IpGeolocationData.model_validate(db_obj, from_attributes=True)

    async def get_by_ip(self, ip: str) -> Optional[IpGeolocationData]:
        """
        Get geolocation data for a specific IP.

        Args:
            ip: The IP address to find

        Returns:
            The geolocation data if found, None otherwise
        """
        async with self.database_client.get_session() as session:
            try:
                result = await session.execute(select(IpGeolocation).where(IpGeolocation.ip == ip))
                data = result.scalar_one_or_none()
                if data is None:
                    return None
                return IpGeolocationData.model_validate(data, from_attributes=True)
            except OperationalError as e:
                logger.error(f"Operational error getting by ip: \n{e}")
                raise DatabaseUnavailableError(f"Database error") from e

    async def get_by_url(self, url: str) -> Optional[IpGeolocationData]:
        """
        Get geolocation data for a specific URL.

        Args:
            url: The URL to find

        Returns:
            The geolocation data if found, None otherwise
        """
        async with self.database_client.get_session() as session:
            try:
                result = await session.execute(
                    select(IpGeolocation).where(IpGeolocation.url == url)
                )
                data = result.scalar_one_or_none()
                if data is None:
                    return None
                return IpGeolocationData.model_validate(data, from_attributes=True)
            except OperationalError as e:
                logger.error(f"Operational error getting by url: \n{e}")
                raise DatabaseUnavailableError(f"Database error") from e

    async def delete_by_ip(self, ip: str) -> bool:
        """
        Delete geolocation data for a specific IP.

        Args:
            ip: The IP address to delete

        Returns:
            True if deleted, False if not found
        """
        async with self.database_client.get_session() as session:
            try:
                result = await session.execute(delete(IpGeolocation).where(IpGeolocation.ip == ip))
                await session.commit()
                return result.rowcount > 0
            except OperationalError as e:
                await session.rollback()
                logger.error(f"Operational error deleting by ip: \n{e}")
                raise DatabaseUnavailableError(f"Database error") from e

    async def delete_by_url(self, url: str) -> bool:
        """
        Delete geolocation data for a specific URL.

        Args:
            url: The URL to delete

        Returns:
            True if deleted, False if not found
        """
        async with self.database_client.get_session() as session:
            try:
                result = await session.execute(
                    delete(IpGeolocation).where(IpGeolocation.url == url)
                )
                await session.commit()
                return result.rowcount > 0
            except OperationalError as e:
                await session.rollback()
                logger.error(f"Operational error deleting by url: \n{e}")
                raise DatabaseUnavailableError(f"Database error") from e

    async def is_available(self) -> bool:
        """
        Check if the repository is available.

        Returns:
            True if the database is available, False if an operational error occurs or an unexpected error occurs.
        """
        async with self.database_client.get_session() as session:
            try:
                await session.execute(select(1))
                return True
            except OperationalError as e:
                logger.error(f"[DB Health] Operational error: {e}")
                return False
            except Exception as e:
                logger.error(f"[DB Health] Unexpected error: {traceback.format_exc()}")
                return False
