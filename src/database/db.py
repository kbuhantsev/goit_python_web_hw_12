from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from settings import settings

engine = create_async_engine(settings.get_uri())
SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency
async def get_session():
    async with SessionLocal() as session:
        yield session
