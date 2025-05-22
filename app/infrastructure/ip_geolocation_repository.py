import socket
import traceback
from typing import Optional

import asyncpg  # type: ignore
from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.sql.expression import literal_column

from app.core.logging import get_logger
from app.domain.models.ip_data import Geolocation
from app.domain.repositories import IpGeolocationRepository, UpsertResult
from app.infrastructure.database import DatabaseClient, DatabaseUnavailableError
from app.infrastructure.models import IpGeolocation

logger = get_logger(__name__)


CONNECTION_ERRORS = (
    asyncpg.PostgresError,
    socket.gaierror,
    ConnectionRefusedError,
    TimeoutError,
    OSError,
    OperationalError,
    IntegrityError,
)


class IpGeolocationRepositoryImpl(IpGeolocationRepository):

    def __init__(self, database_client: DatabaseClient):
        self.database_client = database_client

    async def upsert(self, ip_data: Geolocation) -> tuple[Geolocation, UpsertResult]:
        """
        Upsert (insert or update) IP geolocation data into the database.

        Args:
            ip_data: The geolocation data to upsert

        Returns:
            A tuple containing the upserted geolocation data and the result of the operation

        Raises:
            DatabaseUnavailableError: If the database is unavailable or an unexpected error occurs
        """
        logger.info(f"Upserting IP geolocation data for {ip_data.ip}")
        async with self.database_client.get_session() as session:
            try:
                payload_for_db = ip_data.model_dump(exclude_unset=True)

                values_for_insert = {
                    k: v for k, v in payload_for_db.items() if k not in ["created_at", "updated_at"]
                }

                insert_stmt = pg_insert(IpGeolocation).values(**values_for_insert)

                update_fields_for_set_clause = {
                    key: getattr(insert_stmt.excluded, key)
                    for key in payload_for_db.keys()
                    if key not in ["id", "ip", "created_at", "updated_at"]
                }

                if not update_fields_for_set_clause:
                    set_clause = {"ip": getattr(insert_stmt.excluded, "ip")}
                else:
                    set_clause = update_fields_for_set_clause

                conflict_handling_stmt = insert_stmt.on_conflict_do_update(
                    index_elements=["ip"], set_=set_clause  # Conflict on the 'ip' column
                )

                returning_stmt = conflict_handling_stmt.returning(
                    IpGeolocation, literal_column("xmax")
                )  # type: ignore

                result_row = (await session.execute(returning_stmt)).one_or_none()

                if result_row is None:
                    logger.error(
                        f"Upsert for IP {ip_data.ip} returned no rows. This is unexpected."
                    )
                    raise DatabaseUnavailableError(
                        f"Upsert operation failed to return a row for IP {ip_data.ip}."
                    )

                db_obj, xmax_val = result_row  # Unpack ORM object and xmax

                # For PostgreSQL, xmax = 0 indicates an INSERT, non-zero indicates an UPDATE
                operation_result = UpsertResult.CREATED if xmax_val == 0 else UpsertResult.UPDATED

                await session.commit()
                # No explicit refresh needed here as .returning() gives the final state from DB.

                logger.info(
                    f"Upserted IP geolocation data for {ip_data.ip}: "
                    f"{db_obj}, Action: {operation_result}"
                )

                return Geolocation.model_validate(db_obj, from_attributes=True), operation_result

            except CONNECTION_ERRORS as e:
                await session.rollback()
                logger.error(f"Database error during upsert: \n{e}")
                raise DatabaseUnavailableError("Database integrity or operational error") from e
            except Exception as e:
                await session.rollback()
                logger.error(f"Unexpected error during upsert: \n{traceback.format_exc()}")
                raise

    async def add(self, ip_data: Geolocation) -> Geolocation:
        """
        Add new IP geolocation data to the repository.

        Args:
            ip_data: The geolocation data to add

        Returns:
            The added geolocation data with any generated fields
        """
        logger.info(f"Adding IP data for {ip_data.ip}")
        async with self.database_client.get_session() as session:
            try:
                db_obj = IpGeolocation(**ip_data.model_dump())
                session.add(db_obj)
                await session.commit()
                await session.refresh(db_obj)
                return Geolocation.model_validate(db_obj, from_attributes=True)

            except CONNECTION_ERRORS as e:
                await session.rollback()
                logger.error(f"Database error adding: \n{e}")
                raise DatabaseUnavailableError("Database integrity error") from e
            except Exception as e:
                await session.rollback()
                logger.error(f"Unexpected error adding: \n{traceback.format_exc()}")
                raise

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
        logger.info(f"Updating IP data for {ip_data.ip}")
        async with self.database_client.get_session() as session:
            try:
                result = await session.execute(
                    select(IpGeolocation).where(IpGeolocation.ip == ip_data.ip)
                )
                existing = result.scalar_one_or_none()
                if existing is None:
                    raise ValueError(f"Record with IP {ip_data.ip} does not exist")
                # Update record
                for key, value in ip_data.model_dump().items():
                    setattr(existing, key, value)
                await session.commit()
                await session.refresh(existing)
                return Geolocation.model_validate(existing, from_attributes=True)
            except CONNECTION_ERRORS as e:
                await session.rollback()
                logger.error(f"Database error updating: \n{e}")
                raise DatabaseUnavailableError("Database integrity error") from e
            except Exception as e:
                await session.rollback()
                logger.error(f"Unexpected error updating: \n{traceback.format_exc()}")
                raise

    async def exists_by_ip(self, ip: str) -> bool:
        """
        Check if geolocation data exists for a specific IP.

        Args:
            ip: The IP address to check

        Returns:
            True if exists, False otherwise
        """
        logger.info(f"Checking existence of IP {ip}")
        async with self.database_client.get_session() as session:
            try:
                executed_result = await session.execute(
                    select(IpGeolocation).where(IpGeolocation.ip == ip)
                )
                # Use a new variable for the boolean result
                ip_exists = executed_result.scalar_one_or_none() is not None
                logger.info(f"Checked existence of IP {ip} result: {ip_exists}")
                return ip_exists
            except OperationalError as e:
                logger.error(f"Operational error checking existence: \n{e}")
                raise DatabaseUnavailableError("Database is unavailable") from e

    async def exists_by_url(self, url: str) -> bool:
        """
        Check if geolocation data exists for a specific URL.

        Args:
            url: The URL to check

        Returns:
            True if exists, False otherwise
        """
        logger.info(f"Checking existence of URL {url}")
        async with self.database_client.get_session() as session:
            try:
                executed_result = await session.execute(
                    select(IpGeolocation).where(IpGeolocation.url == url)
                )
                # Use a new variable for the boolean result
                url_exists = executed_result.scalar_one_or_none() is not None
                logger.info(f"Checked existence of URL {url} result: {url_exists}")
                return url_exists
            except OperationalError as e:
                logger.error(f"Operational error checking existence: \n{e}")
                raise DatabaseUnavailableError("Database is unavailable") from e

    async def get_by_ip(self, ip: str) -> Optional[Geolocation]:
        """
        Get geolocation data for a specific IP.

        Args:
            ip: The IP address to find

        Returns:
            The geolocation data if found, None otherwise
        """
        logger.info(f"Getting IP data for {ip}")
        async with self.database_client.get_session() as session:
            try:
                result = await session.execute(select(IpGeolocation).where(IpGeolocation.ip == ip))
                data = result.scalars().first()
                if data is None:
                    logger.warning(f"No data found for {ip}")
                    return None
                return Geolocation.model_validate(data, from_attributes=True)
            except CONNECTION_ERRORS as e:
                logger.error(f"Database connectivity issue: {e}")
                raise DatabaseUnavailableError("Database is unavailable") from e

    async def get_by_url(self, url: str) -> Optional[Geolocation]:
        """
        Get geolocation data for a specific URL.

        Args:
            url: The URL to find

        Returns:
            The geolocation data if found, None otherwise
        """
        logger.info(f"Getting URL data for {url}")
        async with self.database_client.get_session() as session:
            try:
                result = await session.execute(
                    select(IpGeolocation).where(IpGeolocation.url == url)
                )
                data = result.scalars().first()
                if data is None:
                    logger.warning(f"No data found for {url}")
                    return None
                return Geolocation.model_validate(data, from_attributes=True)
            except CONNECTION_ERRORS as e:
                logger.error(f"Database connectivity issue: {e}")
                raise DatabaseUnavailableError("Database is unavailable") from e

    async def delete_by_ip(self, ip: str) -> bool:
        """
        Delete geolocation data for a specific IP.

        Args:
            ip: The IP address to delete

        Returns:
            True if deleted, False if not found
        """
        logger.info(f"Deleting IP data for {ip}")
        async with self.database_client.get_session() as session:
            try:
                result = await session.execute(delete(IpGeolocation).where(IpGeolocation.ip == ip))
                await session.commit()
                return result.rowcount > 0
            except CONNECTION_ERRORS as e:
                await session.rollback()
                logger.error(f"Database connectivity issue: {e}")
                raise DatabaseUnavailableError("Database is unavailable") from e

    async def delete_by_url(self, url: str) -> bool:
        """
        Delete geolocation data for a specific URL.

        Args:
            url: The URL to delete

        Returns:
            True if deleted, False if not found
        """
        logger.info(f"Deleting URL data for {url}")
        async with self.database_client.get_session() as session:
            try:
                result = await session.execute(
                    delete(IpGeolocation).where(IpGeolocation.url == url)
                )
                await session.commit()
                return result.rowcount > 0
            except CONNECTION_ERRORS as e:
                await session.rollback()
                logger.error(f"Database connectivity issue: {e}")
                raise DatabaseUnavailableError("Database is unavailable") from e

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
            except CONNECTION_ERRORS as e:
                logger.error(f"[DB Health] Database connectivity issue: {e}")
                return False
            except Exception as e:
                logger.error(f"[DB Health] Unexpected error: {traceback.format_exc()}")
                return False
