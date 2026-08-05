from Database import users_collection,orders_collection
from pymongo.errors import PyMongoError


async def fetcing_dataa(query: dict):
    try:
        doc = await users_collection.find_one(query or {})
        return doc

    except PyMongoError as e:
        print(f"Fetch failed: {e}")
        return None           
            


async def fetching_order(filter_query: dict):
    try:
            return await orders_collection.find_one(filter_query)
    
    except PyMongoError as e:
            
            print(f"Fetch failed: {e}")
            return None           
                

async def fetching_all_orders():
    cursor = orders_collection.find({})
    return [doc async for doc in cursor]   