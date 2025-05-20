from typing import Optional

import httpx
from pydantic import ValidationError

from app.core.logging import get_logger
from app.domain.models.ip_data import Geolocation
from app.domain.services import IpGeolocationService, IpGeolocationServiceError

logger = get_logger(__name__)


class IpStackGeolocationService(IpGeolocationService):
    def __init__(self, api_key: str):
        self.api_key = api_key

    async def get_geolocation_by_ip(self, ip_address: str) -> Optional[Geolocation]:
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
        url = f"http://api.ipstack.com/{ip_address}?access_key={self.api_key}"
        return await self.__get_geolocation_data(url)

    async def get_geolocation_by_url(self, url: str) -> Optional[Geolocation]:
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
        url = f"http://api.ipstack.com/{url}?access_key={self.api_key}"
        return await self.__get_geolocation_data(url)

    async def __get_geolocation_data(self, url: str) -> Optional[Geolocation]:
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
            logger.info(f"[IpStack] Requesting geolocation data from: {url.split('?')[0]}")
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                logger.info(f"[IpStack] Response status code: {response.status_code}")

                if response.status_code == 200:
                    try:
                        data = response.json()
                        logger.info(f"[IpStack] Response data: {data}")

                        # Check for API error response
                        if "error" in data:
                            error_info = data["error"]
                            logger.warning(f"[IpStack] API returned error: {error_info}")
                            raise IpGeolocationServiceError(
                                f"API error: {error_info.get('info', 'Unknown error')}"
                            )

                        # Validate required fields
                        required_fields = ["ip", "latitude", "longitude"]
                        missing_fields = [field for field in required_fields if not data.get(field)]
                        if missing_fields:
                            logger.warning(f"[IpStack] Missing required fields: {missing_fields}")
                            raise IpGeolocationServiceError(
                                f"Invalid response: missing required fields {missing_fields}"
                            )

                        # Map ipstack fields to our model fields
                        mapped_data = {
                            "ip": data.get("ip"),
                            "latitude": data.get("latitude"),
                            "longitude": data.get("longitude"),
                            "city": data.get("city"),
                            "region": data.get("region_name"),  # ipstack uses region_name
                            "country": data.get("country_name"),  # ipstack uses country_name
                            "continent": data.get("continent_name"),  # ipstack uses continent_name
                            "postal_code": data.get("zip"),  # ipstack uses zip
                        }

                        logger.debug(f"[IpStack] Mapped data: {mapped_data}")
                        return Geolocation(**mapped_data)
                    except ValidationError as json_error:
                        response_text = response.text
                        logger.error(f"[IpStack] Invalid JSON response: {response_text}")
                        raise IpGeolocationServiceError(f"Invalid JSON response: {json_error}")
                else:
                    response_text = response.text
                    logger.warning(
                        f"[IpStack] Failed to get IP data: {response.status_code}, "
                        f"body: {response_text}"
                    )
                    raise IpGeolocationServiceError(
                        f"Failed to get IP data: {response.status_code}"
                    )
        except httpx.RequestError as e:
            logger.error(f"[IpStack] Network error while getting geolocation data: {e}")
            raise IpGeolocationServiceError(f"Network error: {e}")
        except Exception as e:
            logger.error(f"[IpStack] Unexpected error while getting geolocation data: {e}")
            raise IpGeolocationServiceError(f"Unexpected error: {e}")

    async def is_available(self) -> bool:
        """
        Check if the external geolocation service is available.

        Returns:
            True if the service is available, False otherwise.
        Raises:
            IpGeolocationServiceUnavailableError: If the external service is not available.
        Note:
            ipstack returns error code 101 in response body if the
            API key is missing, which means the service is up.
        """
        try:
            url = "https://api.ipstack.com/check"
            logger.info(f"[IpStack Health] Checking service availability at {url}")
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                logger.info(f"[IpStack Health] Response status code: {response.status_code}")

                if response.status_code == 200:
                    data = response.json()
                    if data.get("error", {}).get("code") == 101:
                        logger.info("[IpStack Health] Service is available (missing API key)")
                        return True
                    else:
                        logger.warning(
                            f"[IpStack Health] Service returned unexpected error: {data}"
                        )
                        return False
                else:
                    logger.warning(
                        f"[IpStack Health] Service returned unexpected status code: "
                        f"{response.status_code}"
                    )
                    return False
        except Exception as e:
            logger.error(
                f"[IpStack Health] Failed to check if the service is available: "
                f"\n{e} \nassuming service is unavailable"
            )
            return False
