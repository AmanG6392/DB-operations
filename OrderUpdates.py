from ShippingDetails import pg_pool


async def get_last_modified(order_id: str):
    conn = await pg_pool.acquire()
    try:
        row = await conn.fetchrow(
            "SELECT MAX(event_timestamp) as last_modified FROM order_updates WHERE order_id = $1",
            order_id
        )
        if row["last_modified"]:
            return row["last_modified"]
        return None
    finally:
        await pg_pool.release(conn)


async def add_order_update(order_id: str, status: str, location: str = None):
    conn = await pg_pool.acquire()
    try:
        await conn.execute(
            "INSERT INTO order_updates (order_id, status, location, event_timestamp) VALUES ($1, $2, $3, NOW())",
            order_id, status, location
        )
    finally:
        await pg_pool.release(conn)