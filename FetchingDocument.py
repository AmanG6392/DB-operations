from Database import users_collection
from pymongo.errors import PyMongoError


async def fetcing_dataa(query: dict):
    try:
        doc = await users_collection.find_one(query or {})
        return doc

    except PyMongoError as e:
        print(f"Fetch failed: {e}")
        return None           
            


    