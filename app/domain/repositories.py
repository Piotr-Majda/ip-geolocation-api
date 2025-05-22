from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional

from app.domain.models.ip_data import Geolocation


class RepositoryError(Exception):
    """
    Exception raised when an error occurs in the repository.
    """

    pass


class ConflictOnUpsertInDatabase(RepositoryError):
    """
    Exception raised when a conflict occurs on an upsert operation in the database.
    """

    pass


class UpsertResult(str, Enum):
    """
    Enum for upsert operation result.
    """

    CREATED = "created"
    UPDATED = "updated"


class IpGeolocationRepository(ABC):
    """
    Repository interface for IP geolocation data.
    """

    @abstractmethod
    async def upsert(self, ip_data: Geolocation) -> tuple[Geolocation, UpsertResult]:
        """
        Upsert IP geolocation data in the repository.
        """
        pass

    @abstractmethod
    async def add(self, ip_data: Geolocation) -> Geolocation:
        """
        Add new IP geolocation data to the repository.

        Args:
            ip_data: The IP geolocation data to add

        Returns:
            The added IP geolocation data
        """
        pass

    @abstractmethod
    async def update(self, ip_data: Geolocation) -> Geolocation:
        """
        Update IP geolocation data in the repository.

        Args:
            ip_data: The IP geolocation data to update

        Returns:
            The updated IP geolocation data
        """
        pass

    @abstractmethod
    async def get_by_ip(self, ip: str) -> Optional[Geolocation]:
        """
        Get IP geolocation data by IP address.

        Args:
            ip: The IP address to get data for

        Returns:
            The IP geolocation data if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_by_url(self, url: str) -> Optional[Geolocation]:
        """
        Get IP geolocation data by URL.

        Args:
            url: The URL to get data for

        Returns:
            The IP geolocation data if found, None otherwise
        """
        pass

    @abstractmethod
    async def delete_by_ip(self, ip: str) -> bool:
        """
        Delete IP geolocation data by IP address.

        Args:
            ip: The IP address to delete

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    async def delete_by_url(self, url: str) -> bool:
        """
        Delete IP geolocation data by URL.

        Args:
            url: The URL to delete

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    async def exists_by_ip(self, ip: str) -> bool:
        """
        Check if IP geolocation data exists by IP address.

        Args:
            ip: The IP address to check

        Returns:
            True if exists, False otherwise
        """
        pass

    @abstractmethod
    async def exists_by_url(self, url: str) -> bool:
        """
        Check if IP geolocation data exists by URL.

        Args:
            url: The URL to check

        Returns:
            True if exists, False otherwise
        """
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        """
        Check if the repository is available.

        Returns:
            True if the repository is available, False otherwise.
        """
        pass
