# app/dependencies.py
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get database URL from .env (or fallback for local testing)
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not set in .env file")

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,               # Set to True during debugging to see SQL queries
    future=True
)

# Session factory for dependency injection
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


# Dependency to get DB session in endpoints
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session