from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.infrastructure.models import Base


class DatabaseUnavailableError(Exception):
    pass


class DatabaseClient:
    def __init__(self, url: str):
        self.url = url
        self.engine = None

    def connect(self):
        self.engine = create_async_engine(self.url, echo=False)

    async def close(self):
        if self.engine:
            await self.engine.dispose()
            self.engine = None

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
