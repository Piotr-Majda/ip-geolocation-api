import asyncio
from app.infrastructure.database import DatabaseClient
from app.infrastructure.models import IpGeolocation
from app.core.config import settings


async def main():
    db = DatabaseClient(url=settings.DATABASE_URL)
    try:
        db.connect()
        async with db.get_session() as session:
            entry = IpGeolocation(
                ip="8.8.8.8",
                url="https://example.com/",
                latitude=37.386,
                longitude=-122.0838,
                city="Mountain View",
                region="California",
                country="United States",
                continent="North America",
                postal_code="94035",
            )
            session.add(entry)
            await session.commit()
    finally:
        await db.close()

if __name__ == "__main__":
    asyncio.run(main())
