from Database import users_collection
from pymongo.errors import PyMongoError


async def insert_document(document: dict):
    try:
        result = await users_collection.insert_one(document)

        print("the document is inserted!! hurrayh")
        
        return str(result.inserted_id)

    except PyMongoError as e:
        print(f"document not inserted!! {e}")
        return None