import asyncpg
from config import DATABASE_URL

pool = None


async def connect_db():
    global pool

    if pool is None:
        pool = await asyncpg.create_pool(
            dsn=DATABASE_URL,
            min_size=1,
            max_size=20,
            command_timeout=60,
        )

        print("✅ PostgreSQL Connected")

    return pool


async def close_db():
    global pool

    if pool:
        await pool.close()
        pool = None

        print("❌ PostgreSQL Closed")


async def execute(query: str, *args):
    async with pool.acquire() as conn:
        return await conn.execute(query, *args)


async def fetch(query: str, *args):
    async with pool.acquire() as conn:
        return await conn.fetch(query, *args)


async def fetchrow(query: str, *args):
    async with pool.acquire() as conn:
        return await conn.fetchrow(query, *args)


async def fetchval(query: str, *args):
    async with pool.acquire() as conn:
        return await conn.fetchval(query, *args)
