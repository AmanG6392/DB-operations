import os
import asyncio
import random
from datetime import timedelta
from dotenv import load_dotenv

from faker import Faker

from Database import orders_collection, client
from ShippingDetails import connect_pg, close_pg, pg_pool
import ShippingDetails  # to access pg_pool live after connect_pg()

load_dotenv()
fake = Faker()

ORDER_STATUSES = ["PROCESSING", "SHIPPED", "DELIVERED", "CANCELLED"]
CARRIERS = ["FedEx", "UPS", "DHL", "BlueDart", "Delhivery"]
SERVICE_LEVELS = ["Standard", "Overnight", "Two-Day", "Economy"]
UPDATE_STATUSES = ["ORDER_CREATED", "PACKED", "SHIPPED", "OUT_FOR_DELIVERY", "DELIVERED"]

NUM_ORDERS = 1000


def generate_fake_order(index: int):
    order_id = f"ORD-{100000 + index}"
    created = fake.date_time_between(start_date="-60d", end_date="now")

    # ---- Mongo document (no shippingDetails) ----
    mongo_doc = {
        "orderId": order_id,
        "customerId": f"CUST-{fake.random_int(min=100000, max=999999)}",
        "orderStatus": random.choice(ORDER_STATUSES),
        "timestamps": {
            "created": created.isoformat() + "Z",
            "updated": (created + timedelta(minutes=15)).isoformat() + "Z",
            "estimatedDelivery": (created + timedelta(days=7)).isoformat() + "Z",
        },
        "payment": {
            "method": random.choice(["CREDIT_CARD", "DEBIT_CARD", "UPI", "NET_BANKING"]),
            "transactionId": f"TXN-{fake.random_int(min=100000000, max=999999999)}",
            "billingAddress": {"isSameAsShipping": True},
            "breakdown": {
                "subtotal": round(random.uniform(200, 5000), 2),
                "tax": round(random.uniform(10, 500), 2),
                "shippingCost": round(random.uniform(0, 100), 2),
                "discountsApplied": [],
                "total": 0,
            },
        },
        "items": [
            {
                "productId": f"PROD-{fake.random_int(min=1000, max=9999)}",
                "sku": fake.bothify(text="SKU-???-###"),
                "quantity": random.randint(1, 5),
                "unitPrice": round(random.uniform(50, 2000), 2),
                "productDetails": {
                    "name": fake.word().title() + " " + random.choice(["Laptop", "Shoes", "Watch", "Bag", "Phone"]),
                    "category": [fake.word().title() for _ in range(2)],
                },
            }
        ],
        "auditLog": [
            {"action": "ORDER_CREATED", "user": "system", "timestamp": created.isoformat() + "Z"}
        ],
        "metadata": {
            "sourcePlatform": random.choice(["Web", "Mobile", "App"]),
            "campaignId": f"CAMP-{fake.random_int(min=100, max=999)}",
            "abTestGroup": random.choice(["Variant-A", "Variant-B"]),
        },
    }

    breakdown = mongo_doc["payment"]["breakdown"]
    breakdown["total"] = round(
        breakdown["subtotal"] + breakdown["tax"] + breakdown["shippingCost"], 2
    )

    # ---- Postgres: shipping_details row ----
    shipping_row = (
        order_id,
        fake.street_address(),
        fake.city(),
        fake.state_abbr(),
        fake.postcode(),
        "USA",
        float(fake.latitude()),
        float(fake.longitude()),
        random.choice(CARRIERS),
        random.choice(SERVICE_LEVELS),
    )

    # ---- Postgres: order_updates rows ----
    # Generate a short status history so get_last_modified has real data
    num_updates = random.randint(1, 3)
    update_rows = []
    ts = created
    for i in range(num_updates):
        status = UPDATE_STATUSES[min(i, len(UPDATE_STATUSES) - 1)]
        ts = ts + timedelta(hours=random.randint(1, 24))
        update_rows.append((order_id, status, fake.city(), ts))

    return mongo_doc, shipping_row, update_rows


async def seed_orders():
    await connect_pg()
    pool = ShippingDetails.pg_pool

    mongo_docs = []
    shipping_rows = []
    update_rows = []

    for i in range(NUM_ORDERS):
        doc, ship_row, upd_rows = generate_fake_order(i)
        mongo_docs.append(doc)
        shipping_rows.append(ship_row)
        update_rows.extend(upd_rows)

    # ---- 1. Bulk insert into Mongo ----
    result = await orders_collection.insert_many(mongo_docs)
    print(f"Inserted {len(result.inserted_ids)} orders into MongoDB")

    # ---- 2. Bulk insert into shipping_details ----
    async with pool.acquire() as conn:
        await conn.executemany(
            """
            INSERT INTO shipping_details
                (order_id, street, city, state, postal_code, country, lat, lng, carrier, service_level)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            """,
            shipping_rows,
        )
    print(f"Inserted {len(shipping_rows)} rows into shipping_details")

    # ---- 3. Bulk insert into order_updates ----
    async with pool.acquire() as conn:
        await conn.executemany(
            """
            INSERT INTO order_updates (order_id, status, location, event_timestamp)
            VALUES ($1, $2, $3, $4)
            """,
            update_rows,
        )
    print(f"Inserted {len(update_rows)} rows into order_updates")

    await close_pg()
    await client.close()


if __name__ == "__main__":
    asyncio.run(seed_orders())