import typing as t
from functools import wraps

import asyncpg

from config import Config

class Database:
    def __init__(self) -> None:
        self.dsn = Config.env('DB_DSN')

    async def connect(self) -> None:
        self.pool = await asyncpg.create_pool(self.dsn)

    async def close(self) -> None:
        await self.pool.close()

    def accquire_connection(func: t.Callable[..., t.Any]) -> t.Callable[..., t.Any]:
        @wraps(func)
        async def wrapper(self: 'Database', *args: t.Any) -> t.Any:
            async with self.pool.acquire() as conn:
                return await func(self, *args, conn = conn)
        return wrapper

    @accquire_connection
    async def fetch_value(self, query: str, *values: t.Any, conn: asyncpg.Connection) -> t.Any:
        statement = await conn.prepare(query)
        data = await statement.fetchval(*values)
        return data

    @accquire_connection
    async def fetch_row(self, query: str, *values: t.Any, conn: asyncpg.Connection) -> t.Optional[dict[str, t.Any]]:
        statement = await conn.prepare(query)
        if data := await statement.fetchrow(*values):
            return vars(data)
        return None

    @accquire_connection
    async def fetch_rows(self, query: str, *values: t.Any, conn: asyncpg.Connection) -> t.Optional[list[dict[str, t.Any]]]:
        statement = await conn.prepare(query)
        if data := await statement.fetch(*values):
            return [vars(row) for row in data]
        return None

    @accquire_connection
    async def fetch_column(self, query: str, *values: t.Any, conn: asyncpg.Connection) -> list[t.Any]:
        statement = await conn.prepare(query)
        data = await statement.fetch(*values)
        return [row[0] for row in data]

    @accquire_connection
    async def execute(self, query: str, *values: t.Any, conn: asyncpg.Connection) -> None:
        statement = await conn.prepare(query)
        await statement.fetch(*values)