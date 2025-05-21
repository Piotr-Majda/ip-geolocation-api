from typing import Optional

from app.core.logging import get_logger
from app.domain.models.ip_data import Geolocation
from app.domain.repositories import IpGeolocationRepository
from app.domain.services import IpGeolocationService

logger = get_logger(__name__)


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

    async def get_ip_data(self, ip: str) -> Optional[Geolocation]:
        """
        Get geolocation data for an IP.

        Args:
            ip: The IP address to get data for

        Returns:
            The geolocation data if found, None otherwise
        """
        logger.info(f"Getting IP data for {ip}")
        result = await self.repository.get_by_ip(ip)
        logger.info(f"Got IP data for {ip}")
        return result

    async def get_url_data(self, url: str) -> Optional[Geolocation]:
        """
        Get geolocation data for an URL.

        Args:
            url: The URL to get data for

        Returns:
            The geolocation data if found, None otherwise
        """
        logger.info(f"Getting URL data for {url}")
        result = await self.repository.get_by_url(url)
        logger.info(f"Got URL data for {url}")
        return result

    async def add_ip_data(self, ip_address: str) -> Geolocation:
        """
        Add or update geolocation data in the repository.
        If the IP already exists, update its data.

        Args:
            ip_address: The IP address to add or update

        Returns:
            The geolocation data

        Raises:
            NotFoundGeolocationData: If the IP data is not found in external service
        """
        logger.info(f"Adding IP data for {ip_address}")
        ip_data = await self.external_service.get_geolocation_by_ip(ip_address)
        if ip_data is None:
            logger.error(f"IP data not found for {ip_address}")
            raise NotFoundGeolocationData("IP data not found")

        # Check if record exists
        if await self.repository.exists_by_ip(ip_address):
            # Update existing record
            updated_data = await self.repository.update(ip_data)
            logger.info(f"Updated IP data for {ip_address}")
            return updated_data
        else:
            # Add new record
            added_data = await self.repository.add(ip_data)
            logger.info(f"Added IP data for {ip_address}")
            return added_data

    async def add_url_data(self, url: str) -> Geolocation:
        """
        Add or update geolocation data in the repository.
        If the URL already exists, update its data.

        Args:
            url: The URL to add or update

        Returns:
            The geolocation data

        Raises:
            NotFoundGeolocationData: If the URL data is not found in external service
        """
        logger.info(f"Adding URL data for {url}")
        ip_data = await self.external_service.get_geolocation_by_url(url)
        if ip_data is None:
            logger.error(f"IP data not found for {url}")
            raise NotFoundGeolocationData("IP data not found on external service")
        if ip_data.url != url:
            ip_data.url = url

        # Check if record exists
        if await self.repository.exists_by_url(url):
            # Update existing record
            updated_data = await self.repository.update(ip_data)
            logger.info(f"Updated URL data for {url}")
            return updated_data
        else:
            # Add new record
            added_data = await self.repository.add(ip_data)
            logger.info(f"Added URL data for {url}")
            return added_data

    async def delete_ip_data(self, ip: str) -> bool:
        """
        Delete geolocation data from the repository.

        Args:
            ip: The IP address to delete

        Returns:
            True if deleted, False if not found
        """
        logger.info(f"Deleting IP data for {ip}")
        result = await self.repository.delete_by_ip(ip)
        logger.info(f"Deleted IP data for {ip}")
        return result

    async def delete_url_data(self, url: str) -> bool:
        """
        Delete geolocation data from the repository.

        Args:
            url: The URL to delete

        Returns:
            True if deleted, False if not found
        """
        logger.info(f"Deleting URL data for {url}")
        result = await self.repository.delete_by_url(url)
        logger.info(f"Deleted URL data for {url}")
        return result
