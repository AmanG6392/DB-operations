import os
from dotenv import load_dotenv
import asyncpg

load_dotenv()

NEON_URL = os.getenv("NEON_DB_URL")

pg_pool: asyncpg.Pool | None = None


async def connect_pg():
    global pg_pool
    pg_pool = await asyncpg.create_pool(NEON_URL, min_size=1, max_size=5)
    return pg_pool


async def close_pg():
    global pg_pool
    if pg_pool:
        await pg_pool.close()


def reshape_shipping(row: dict) -> dict:
    return {
        "address": {
            "street": row["street"],
            "city": row["city"],
            "state": row["state"],
            "postalCode": row["postal_code"],
            "country": row["country"],
            "coordinates": {
                "lat": row["lat"],
                "lng": row["lng"],
            },
        },
        "method": {
            "carrier": row["carrier"],
            "serviceLevel": row["service_level"],
            "trackingHistory": [],
        },
    }


async def get_shipping_details(order_id: str) -> dict | None:
    if pg_pool is None:
        raise RuntimeError("Postgres pool not initialized — please use connect_pg() at beggining.")

    async with pg_pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM shipping_details WHERE order_id = $1", order_id
        )

    return reshape_shipping(dict(row)) if row else None