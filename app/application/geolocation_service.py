from typing import List, Optional

from app.domain.models.ip_data import IpGeolocationData
from app.domain.repositories import IpGeolocationRepository
from app.domain.services import IpGeolocationService


class GeolocationApplicationServiceError(Exception):
    """
    Exception for geolocation application service.
    """
    pass


class NotFoundGeolocationData(GeolocationApplicationServiceError):
    """
    Exception for not found geolocation data.
    """
    pass


class GeolocationApplicationService:
    """
    Application service for geolocation operations.

    This service coordinates between the domain repository and external service.
    """

    def __init__(self, repository: IpGeolocationRepository, external_service: IpGeolocationService):
        self.repository = repository
        self.external_service = external_service

    async def get_ip_data(self, ip: str) -> Optional[IpGeolocationData]:
        """
        Get geolocation data for an IP.

        Args:
            ip: The IP address to get data for

        Returns:
            The geolocation data if found, None otherwise
        """
        return await self.repository.get_by_ip(ip)
    
    async def get_url_data(self, url: str) -> Optional[IpGeolocationData]:
        """
        Get geolocation data for an URL.

        Args:
            url: The URL to get data for

        Returns:
            The geolocation data if found, None otherwise
        """
        return await self.repository.get_by_url(url)

    async def add_ip_data(self, ip_address: str) -> IpGeolocationData:
        """
        Add geolocation data to the repository.

        Args:
            ip_address: The IP address to add

        Returns:
            The added geolocation data
        """
        ip_data = await self.external_service.get_geolocation_by_ip(ip_address)
        if ip_data is None:
            raise NotFoundGeolocationData("IP data not found")
        return await self.repository.add(ip_data)
    
    async def add_url_data(self, url: str) -> IpGeolocationData:
        """
        Add geolocation data to the repository.

        Args:
            url: The URL to add

        Returns:
            The added geolocation data
        """
        ip_data = await self.external_service.get_geolocation_by_url(url)
        if ip_data is None:
            raise NotFoundGeolocationData("IP data not found on external service")
        if ip_data.url != url:
            ip_data.url = url
        return await self.repository.add(ip_data)

    async def delete_ip_data(self, ip: str) -> bool:
        """
        Delete geolocation data from the repository.

        Args:
            ip: The IP address to delete

        Returns:
            True if deleted, False if not found
        """
        return await self.repository.delete_by_ip(ip)
    
    async def delete_url_data(self, url: str) -> bool:
        """
        Delete geolocation data from the repository.

        Args:
            ip: The IP address to delete

        Returns:
            True if deleted, False if not found
        """
        return await self.repository.delete_by_url(url)
