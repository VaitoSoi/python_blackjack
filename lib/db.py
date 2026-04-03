import models.game  # noqa: F401, I001

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from lib.env import DB_URL

engine = create_async_engine(DB_URL)
session_maker = async_sessionmaker(engine, expire_on_commit=False)

async def init():
    async with engine.connect() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)
