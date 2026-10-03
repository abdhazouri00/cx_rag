import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from helpers.config import get_settings, get_database_url

async def create_database_if_missing():
  settings = get_settings()

  engine = create_async_engine(get_database_url(settings, database="master"), isolation_level="AUTOCOMMIT")

  async with engine.connect() as connection:
    result = await connection.execute(text("SELECT DB_ID(:name)"), {"name": settings.MSSQL_MAIN_DATABASE})

    if result.scalar() is None:
      await connection.execute(text(f"CREATE DATABASE [{settings.MSSQL_MAIN_DATABASE}]"))

  await engine.dispose()

if __name__ == "__main__":
  asyncio.run(create_database_if_missing())
