from abc import ABC, abstractmethod
from typing import Optional

from app.domain.models.ip_data import IpGeolocationData


class IpGeolocationServiceError(Exception):
    pass


class IpGeolocationServiceUnavailableError(IpGeolocationServiceError):
    pass


class IpGeolocationService(ABC):
    """Interface for retrieving IP geolocation data from external services."""

    @abstractmethod
    async def get_geolocation_by_ip(self, ip_address: str) -> Optional[IpGeolocationData]:
        """
        Retrieve geolocation data for an IP address from an external service.

        Args:
            ip_address: The IP address to look up

        Returns:
            Geolocation data if successfully retrieved, None otherwise
        Raises:
            IpGeolocationServiceUnavailableError: If the external service is not available
            IpGeolocationServiceError: If the external service returns an error or any other error
        """
        pass

    @abstractmethod
    async def get_geolocation_by_url(self, url: str) -> Optional[IpGeolocationData]:
        """
        Retrieve geolocation data for an URL from an external service.

        Args:
            url: The URL to look up

        Returns:
            Geolocation data if successfully retrieved, None otherwise
        Raises:
            IpGeolocationServiceUnavailableError: If the external service is not available
            IpGeolocationServiceError: If the external service returns an error or any other error
        """
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        """
        Check if the external geolocation service is available.

        Returns:
            True if the service is available, False otherwise
        """
        pass
