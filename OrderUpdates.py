import ShippingDetails


async def get_last_modified(order_id: str):
    conn = await ShippingDetails.pg_pool.acquire()
    try:
        row = await conn.fetchrow(
            "SELECT MAX(event_timestamp) as last_modified FROM order_updates WHERE order_id = $1",
            order_id
        )
        if row["last_modified"]:
            return row["last_modified"]
        return None
    finally:
        await ShippingDetails.pg_pool.release(conn)


async def add_order_update(order_id: str, status: str, location: str = None):
    conn = await ShippingDetails.pg_pool.acquire()
    try:
        await conn.execute(
            "INSERT INTO order_updates (order_id, status, location, event_timestamp) VALUES ($1, $2, $3, NOW())",
            order_id, status, location
        )
    finally:
        await ShippingDetails.pg_pool.release(conn)


async def get_global_last_modified():
    conn = await ShippingDetails.pg_pool.acquire()
    try:
        row = await conn.fetchrow(
            "SELECT MAX(event_timestamp) as last_modified FROM order_updates"
        )
        return row["last_modified"] if row["last_modified"] else None
    finally:
        await ShippingDetails.pg_pool.release(conn)        