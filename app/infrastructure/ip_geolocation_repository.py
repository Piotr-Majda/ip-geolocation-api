import traceback
from typing import Optional

from pydantic import ValidationError
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError, OperationalError

from app.core.logging import get_logger
from app.domain.models.ip_data import Geolocation
from app.domain.repositories import IpGeolocationRepository
from app.infrastructure.database import DatabaseClient, DatabaseUnavailableError
from app.infrastructure.models import IpGeolocation

logger = get_logger(__name__)


class IpGeolocationRepositoryImpl(IpGeolocationRepository):

    def __init__(self, database_client: DatabaseClient):
        self.database_client = database_client

    async def add(self, ip_data: Geolocation) -> Geolocation:
        """
        Add new IP geolocation data to the repository.

        Args:
            ip_data: The geolocation data to add

        Returns:
            The added geolocation data with any generated fields
        """
        async with self.database_client.get_session() as session:
            try:
                # Check if record exists
                if await self.exists_by_ip(str(ip_data.ip)):
                    raise ValueError(f"Record with IP {ip_data.ip} already exists")

                # Add new record
                db_obj = IpGeolocation(**ip_data.model_dump())
                session.add(db_obj)
                await session.commit()
                await session.refresh(db_obj)
                return Geolocation.model_validate(db_obj, from_attributes=True)

            except (ValidationError, ValueError) as e:
                logger.error(f"Validation error: {e}")
                raise
            except OperationalError as e:
                await session.rollback()
                logger.error(f"Operational error adding: \n{e}")
                raise DatabaseUnavailableError("Database error") from e
            except IntegrityError as e:
                await session.rollback()
                logger.error(f"Integrity error adding: \n{e}")
                raise DatabaseUnavailableError("Database integrity error") from e
            except Exception as e:
                await session.rollback()
                logger.error(f"Unexpected error adding: \n{traceback.format_exc()}")
                raise DatabaseUnavailableError("Unexpected database error") from e

    async def update(self, ip_data: Geolocation) -> Geolocation:
        """
        Update existing IP geolocation data in the repository.

        Args:
            ip_data: The geolocation data to update

        Returns:
            The updated geolocation data with any generated fields

        Raises:
            ValueError: If the record doesn't exist
        """
        async with self.database_client.get_session() as session:
            try:
                # Get existing record
                result = await session.execute(
                    select(IpGeolocation).where(IpGeolocation.ip == ip_data.ip)
                )
                existing = result.scalar_one_or_none()

                if not existing:
                    raise ValueError(f"Record with IP {ip_data.ip} does not exist")

                # Update record
                for key, value in ip_data.model_dump().items():
                    setattr(existing, key, value)
                await session.commit()
                await session.refresh(existing)
                return Geolocation.model_validate(existing, from_attributes=True)
            except ValueError as e:
                logger.error(f"{e}")
                raise
            except OperationalError as e:
                await session.rollback()
                logger.error(f"Operational error updating: \n{e}")
                raise DatabaseUnavailableError("Database error") from e
            except IntegrityError as e:
                await session.rollback()
                logger.error(f"Integrity error updating: \n{e}")
                raise DatabaseUnavailableError("Database integrity error") from e
            except Exception as e:
                await session.rollback()
                logger.error(f"Unexpected error updating: \n{traceback.format_exc()}")
                raise DatabaseUnavailableError("Unexpected database error") from e

    async def exists_by_ip(self, ip: str) -> bool:
        """
        Check if geolocation data exists for a specific IP.

        Args:
            ip: The IP address to check

        Returns:
            True if exists, False otherwise
        """
        async with self.database_client.get_session() as session:
            try:
                result = await session.execute(select(IpGeolocation).where(IpGeolocation.ip == ip))
                return result.scalar_one_or_none() is not None
            except OperationalError as e:
                logger.error(f"Operational error checking existence: \n{e}")
                raise DatabaseUnavailableError("Database error") from e

    async def exists_by_url(self, url: str) -> bool:
        """
        Check if geolocation data exists for a specific URL.

        Args:
            url: The URL to check

        Returns:
            True if exists, False otherwise
        """
        async with self.database_client.get_session() as session:
            try:
                result = await session.execute(
                    select(IpGeolocation).where(IpGeolocation.url == url)
                )
                return result.scalar_one_or_none() is not None
            except OperationalError as e:
                logger.error(f"Operational error checking existence: \n{e}")
                raise DatabaseUnavailableError("Database error") from e

    async def get_by_ip(self, ip: str) -> Optional[Geolocation]:
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
                return Geolocation.model_validate(data, from_attributes=True)
            except OperationalError as e:
                logger.error(f"Operational error getting by ip: \n{e}")
                raise DatabaseUnavailableError("Database error") from e

    async def get_by_url(self, url: str) -> Optional[Geolocation]:
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
                return Geolocation.model_validate(data, from_attributes=True)
            except OperationalError as e:
                logger.error(f"Operational error getting by url: \n{e}")
                raise DatabaseUnavailableError("Database error") from e

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
                raise DatabaseUnavailableError("Database error") from e

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
                raise DatabaseUnavailableError("Database error") from e

    async def is_available(self) -> bool:
        """
        Check if the repository is available.

        Returns:
            True if the database is available,
            False if an operational error occurs or an unexpected error occurs.
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
