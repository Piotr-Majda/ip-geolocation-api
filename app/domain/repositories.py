from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.models.ip_data import IpGeolocationData


class IpGeolocationRepository(ABC):
    """Interface for IP geolocation data repository."""

    @abstractmethod
    async def add(self, ip_data: IpGeolocationData) -> IpGeolocationData:
        """
        Add new IP geolocation data to the repository.

        Args:
            ip_data: The geolocation data to add

        Returns:
            The added geolocation data with any generated fields
        """
        pass

    @abstractmethod
    async def get_by_ip(self, ip: str) -> Optional[IpGeolocationData]:
        """
        Get geolocation data for a specific IP.

        Args:
            ip: The IP address to find

        Returns:
            The geolocation data if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_by_url(self, url: str) -> Optional[IpGeolocationData]:
        """
        Get geolocation data for a specific URL.

        Args:
            url: The URL to find

        Returns:
            The geolocation data if found, None otherwise
        """
        pass

    @abstractmethod
    async def delete_by_ip(self, ip: str) -> bool:
        """
        Delete geolocation data for a specific IP.

        Args:
            ip: The IP address to delete

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    async def delete_by_url(self, url: str) -> bool:
        """
        Delete geolocation data for a specific URL.

        Args:
            url: The URL to delete

        Returns:
            True if deleted, False if not found
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
