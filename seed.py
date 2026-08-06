import asyncio
from Database import orders_collection,client

order_doc = {
    "orderId": "ORD-987654321",
    "customerId": "CUST-102938",
    "orderStatus": "PROCESSING",

    "timestamps": {
        "created": "2024-10-27T10:00:00Z",
        "updated": "2024-10-27T10:15:00Z",
        "estimatedDelivery": "2024-11-05T00:00:00Z"
    },


    "shippingDetails": {
        "address": {
            "street": "123 Main St",
            "city": "Anytown",
            "state": "CA",
            "postalCode": "90210",
            "country": "USA",
            "coordinates": {"lat": 34.0522, "lng": -118.2437}
        },

        "method": {
            "carrier": "FedEx",
            "serviceLevel": "Overnight",
            "trackingHistory": [
                {"status": "Label Created", "location": "Warehouse A", "timestamp": "2024-10-27T10:30:00Z"}
            ]
        }

    },


    "payment": {
        "method": "CREDIT_CARD",
        "transactionId": "TXN-555444333",
        "billingAddress": {"isSameAsShipping": True},
        "breakdown": {
            "subtotal": 1250.00,
            "tax": 100.00,
            "shippingCost": 25.00,
            "discountsApplied": [
                {"code": "FALL20", "amount": 50.00, "type": "PERCENTAGE"}
            ],
            "total": 1325.00

        }


    },



    "items": [

        {
            "productId": "PROD-A1",
            "sku": "SKU-A1-BLK-M",
            "quantity": 2,
            "unitPrice": 500.00,
            "productDetails": {
                "name": "High-End Laptop",
                "category": ["Electronics", "Computers", "Laptops"],
                "attributes": {
                    "color": "Black",
                    "size": "Medium",
                    "weight": "1.5kg",
                    "dimensions": {"length": 30, "width": 20, "height": 2}
                },

                "warranty": {
                    "provider": "TechCare",
                    "durationMonths": 24,
                    "terms": "Standard limited warranty"
                }

            },


            "customizationOptions": [
                {"type": "Engraving", "value": "Happy Birthday", "cost": 25.00}
            ]
        }


    ],
    "auditLog": [
        {"action": "ORDER_CREATED", "user": "system", "timestamp": "2024-10-27T10:00:00Z"}
    ],
    "metadata": {

        "sourcePlatform": "Web",
        "campaignId": "CAMP-HOLIDAY24",
        "abTestGroup": "Variant-B"

    }


}


async def seed():
    result = await orders_collection.insert_one(order_doc)
    print("Inserted with _id:", result.inserted_id)
    await client.close()

async def create_indexes():
    result = await orders_collection.create_index("orderId", unique=True)
    print(f"Index created: {result}")
    await client.close()


if __name__ == "__main__":
    
    ##asyncio.run(seed())
    asyncio.run(create_indexes())

