from fastapi import FastAPI
from fastapi import HTTPException
from Database import client
from InsertingDocument import insert_document
from FetchingDocument import fetcing_dataa
from bson import ObjectId



app = FastAPI()

@app.on_event("shutdown")
async def shutdown_db_client():
    await client.close()   
    

@app.get("/")
async def document_fetch():
    return {"message":"Welcome to the jungle"}


@app.post("/users/")
async def inserting_Doc(name: str, image_url: str):
    document = {"name" : name, "image_url": image_url}

    insert_id = await insert_document(document)

    print(type(insert_id), insert_id)
    

    if not insert_id:
        raise HTTPException(status_code=500, detail="Insert failed")

    return {"id": insert_id}


@app.get("/users/{user_id}")
async def get_user(user_id: str):
    doc = await fetcing_dataa({"_id": ObjectId(user_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="User not found")
    doc["_id"] = str(doc["_id"])  # convert ObjectId to string for JSON response
    return doc




