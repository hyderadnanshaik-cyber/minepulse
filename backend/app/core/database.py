import os
import ssl
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

Base = declarative_base()

# Configure SSL context for Azure PostgreSQL if connecting to Azure cloud
connect_args = {}
if "azure.com" in settings.DATABASE_URL or os.getenv("AZURE_POSTGRES_SSL", "false").lower() == "true":
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    connect_args["ssl"] = ctx
    logger.info("Configured SSL context for Azure PostgreSQL Flexible Server.")

# Async engine — PostgreSQL 18 with PostGIS / Azure Flexible Server
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=30,
    max_overflow=50,
    pool_timeout=60,
    pool_recycle=1800,
    connect_args=connect_args
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

async_session_factory = AsyncSessionLocal

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an AsyncSession."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
