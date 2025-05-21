import asyncio
import random

from app.infrastructure.database import DatabaseClient
from app.infrastructure.models import IpGeolocation
from app.core.config import settings

cities = ["Mountain View", "San Francisco", "Los Angeles", "San Diego", "San Jose", "San Antonio", "San Francisco", "San Antonio", "San Antonio", "San Antonio"]
regions = ["California", "Texas", "New York", "Florida", "Illinois", "Texas", "New York", "Florida", "Illinois", "Texas"]
countries = ["United States", "Canada", "Mexico", "Brazil", "Argentina", "Chile", "Peru", "Venezuela", "Colombia", "Ecuador"]
continents = ["North America", "South America", "Europe", "Asia", "Africa", "Australia", "Antarctica"]
urls = ["https://wp.com/", "https://wordpress.com/", "https://asp.net/", "https://tv.com/", "https://wix.com/", "https://squarespace.com/", "https://shopify.com/", "https://bigcartel.com/", "https://tumblr.com/", "https://blogger.com/"]

def random_ip():
    return ".".join(str(random.randint(0, 255)) for _ in range(4))

async def main():
    db = DatabaseClient(url=settings.DATABASE_URL)
    try:
        db.connect()
        async with db.get_session() as session:
            # generate random data
            try:
                entires = []
                for _ in range(100):
                    entry = IpGeolocation(
                        ip=random_ip(), 
                        url=random.choice(urls),
                        latitude=random.uniform(-90, 90),
                        longitude=random.uniform(-180, 180),
                        city=random.choice(cities),
                        region=random.choice(regions),
                        country=random.choice(countries),
                        continent=random.choice(continents),
                        postal_code=str(random.randint(10000, 99999)),
                    )
                    entires.append(entry)
                    
                session.add_all(entires)
                await session.commit()
            except Exception as e:
                print(e)
                await session.rollback()
    finally:
        await db.close()

if __name__ == "__main__":
    asyncio.run(main())
