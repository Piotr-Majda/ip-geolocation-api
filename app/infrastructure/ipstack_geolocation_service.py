from typing import Optional

import httpx

from app.domain.services import IpGeolocationService, IpGeolocationServiceError
from app.domain.models.ip_data import IpGeolocationData
from app.core.logging import get_logger

logger = get_logger(__name__)

class IpStackGeolocationService(IpGeolocationService):
    def __init__(self, api_key: str):
        self.api_key = api_key
        
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
        json_schema = IpGeolocationData.model_json_schema()
        url = f"http://api.ipstack.com/{ip_address}?access_key={self.api_key}&callback={json_schema}"
        return await self.__get_geolocation_data(url)

    async def get_geolocation_by_url(self, url: str) -> Optional[IpGeolocationData]:
        """
        Retrieve geolocation data for an URL from an external service.
        Args:
            ip_address: The IP address to look up

        Returns:
            Geolocation data if successfully retrieved, None otherwise
        Raises:
            IpGeolocationServiceUnavailableError: If the external service is not available
            IpGeolocationServiceError: If the external service returns an error or any other error
        """
        json_schema = IpGeolocationData.model_json_schema()
        url = f"http://api.ipstack.com/{url}?access_key={self.api_key}&callback={json_schema}"
        return await self.__get_geolocation_data(url)
        
    async def __get_geolocation_data(self, url: str) -> Optional[IpGeolocationData]:
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
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                if response.status_code == 200:
                    data = await response.json()
                    return IpGeolocationData(**data)
                else:
                    raise IpGeolocationServiceError(f"Failed to get IP data: {response.status_code}")
        except Exception as e:
            raise IpGeolocationServiceError(f"Failed to get IP data: {e}")
    

    async def is_available(self) -> bool:
        """
        Check if the external geolocation service is available.

        Returns:
            True if the service is available, False otherwise.
        Raises:
            IpGeolocationServiceUnavailableError: If the external service is not available.
        Note:
            ipstack returns HTTP 101 if the API key is missing, which means the service is up.
        """
        try:
            url = "https://api.ipstack.com/check"
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                if response.status_code == 101: # Missing API key, but api is available
                    return True
                else:
                    return False
        except Exception as e:
            logger.error(f"[IpStack Health] Failed to check if the service is available: \n{e} \nassuming service is unavailable")
            return False