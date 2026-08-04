import os
import asyncio
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv

from faker import Faker
import asyncpg

from Database import orders_collection, client  # your existing Mongo setup

load_dotenv()
fake = Faker()

NEON_URL = os.getenv("NEON_DB_URL")


ORDER_STATUSES = ["PROCESSING", "SHIPPED", "DELIVERED", "CANCELLED"]
CARRIERS = ["FedEx", "UPS", "DHL", "BlueDart", "Delhivery"]
SERVICE_LEVELS = ["Standard", "Overnight", "Two-Day", "Economy"]

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
                "total": 0,  # filled in below
            },
        },
        
    }

    breakdown = mongo_doc["payment"]["breakdown"]
    breakdown["total"] = round(
        breakdown["subtotal"] + breakdown["tax"] + breakdown["shippingCost"], 2
    )

   
