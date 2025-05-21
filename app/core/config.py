import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    """
    Configuration for the application.
    """

    VERSION: str = "v1"
    PROJECT_NAME: str = "IP Geolocation API"
    DESCRIPTION: str = "API for IP Geolocation"

    ALLOWED_ORIGINS: list[str] = ["*"]

    IPSTACK_API_KEY: str = str(os.getenv("IPSTACK_API_KEY"))
    if not IPSTACK_API_KEY:
        raise ValueError("IPSTACK_API_KEY is not set")

    DATABASE_URL: str = str(os.getenv("DATABASE_URL"))
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL is not set")


settings = Settings()
