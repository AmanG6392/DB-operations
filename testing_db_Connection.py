import asyncio
from Database import client
from pymongo.errors import ConnectionFailure, PyMongoError


async def testing_conn():
    try:
        await client.admin.command('ping')
        print("✅ Successfully connected to MongoDB!")
        return True
    except ConnectionFailure as e:
        print(f"❌ Connection failed: {e}")
        return False


asyncio.run(testing_conn())