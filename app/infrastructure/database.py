from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.logging import get_logger
from app.infrastructure.models import Base

logger = get_logger(__name__)


class DatabaseUnavailableError(Exception):
    pass


class DatabaseClient:
    def __init__(self, url: str):
        self.url = url
        self.engine = None

    def connect(self):
        try:
            logger.info(f"Connecting to database: {self.url}")
            self.engine = create_async_engine(self.url, echo=False)
        except OperationalError as e:
            logger.error(f"Failed to connect to database: {e}")
            raise DatabaseUnavailableError(f"Failed to connect to database: {e}") from e
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise DatabaseUnavailableError(f"Failed to connect to database: {e}") from e

    async def close(self):
        try:
            logger.info(f"Closing database: {self.url}")
            if self.engine:
                await self.engine.dispose()
                self.engine = None
            logger.info(f"Database closed: {self.url}")
        except OperationalError as e:
            logger.error(f"Failed to close database: {e}")
            raise DatabaseUnavailableError(f"Failed to close database: {e}") from e
        except Exception as e:
            logger.error(f"Failed to close database: {e}")
            raise DatabaseUnavailableError(f"Failed to close database: {e}") from e

    async def clean_tables(self):
        if self.engine is None:
            raise DatabaseUnavailableError("Engine is not initialized")
        async with self.get_session() as session:
            try:
                for table in reversed(Base.metadata.sorted_tables):
                    await session.execute(table.delete())
                await session.commit()
            except Exception:
                await session.rollback()

    async def reset_schema(self):
        if self.engine is None:
            raise DatabaseUnavailableError("Engine is not initialized")
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    def get_session(self) -> AsyncSession:
        if self.engine is None:
            raise DatabaseUnavailableError("Engine is not initialized")
        session_factory = async_sessionmaker(self.engine, expire_on_commit=False)
        return session_factory()
