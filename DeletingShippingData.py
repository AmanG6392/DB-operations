## this file only deletea the shipping detail from the already pushed data of shipping details from db 
## it is only one time


import asyncio
from Database import orders_collection, client

async def remove_shipping_details():
    result = await orders_collection.update_one(
        {"orderId": "ORD-987654321"},
        {"$unset": {"shippingDetails": ""}}
    )
    
    await client.close()

if __name__ == "__main__":
    asyncio.run(remove_shipping_details())