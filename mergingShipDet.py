import os
import json
from dotenv import load_dotenv
import asyncpg
import asyncio

from Database import orders_collection, client

load_dotenv()

NEON_URL = os.getenv("NEON_DB_URL")


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


async def get_full_order(order_id: str) -> dict:
    mongo_doc = await orders_collection.find_one({"orderId": order_id}, {"_id": 0})
    if not mongo_doc:
        return {"error": f"No order found for {order_id}"}

    conn = await asyncpg.connect(NEON_URL)
    row = await conn.fetchrow(
        "SELECT * FROM shipping_details WHERE order_id = $1", order_id
    )
    await conn.close()

    mongo_doc["shippingDetails"] = reshape_shipping(dict(row)) if row else None

    return mongo_doc





