import json
import time
from Cache import redis_client
from fastapi import FastAPI, Request, HTTPException
from Database import client
from InsertingDocument import insert_document
from FetchingDocument import fetcing_dataa, fetching_order
from bson import ObjectId
from Dfsiteration import dfsiteration
from fastapi.middleware.gzip import GZipMiddleware
from mergingShipDet import get_full_order
from OrderUpdates import get_last_modified
from ShippingDetails import connect_pg, close_pg, get_shipping_details, get_full_order


app = FastAPI()


app.add_middleware(
    GZipMiddleware,
    minimum_size=1000
)


@app.on_event("startup")
async def startup_pg_pool():
    await connect_pg()                                                                                                              

@app.on_event("shutdown")
async def shutdown_db_client():
    await client.close()  
    await redis_client.close()

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start
    print(f"{request.method} {request.url.path} took {duration*1000:.2f}ms (total)")
    return response

@app.get("/")
async def document_fetch():
    return {"message": "Welcome to the jungle"}

@app.post("/users/")
async def inserting_Doc(name: str, image_url: str):
    document = {"name": name, "image_url": image_url}
    insert_id = await insert_document(document)
    if not insert_id:
        raise HTTPException(status_code=500, detail="Insert failed")
    return {"id": insert_id}

@app.get("/users/{user_id}")
async def get_user(user_id: str):
    doc = await fetcing_dataa({"_id": ObjectId(user_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="User not found")
    
    doc["_id"] = str(doc["_id"])
    return doc


# @app.get("/orders/{order_id}")
# async def get_order(order_id: str):
#     cache_key = f"order:{order_id}"

#     # 1. Check Redis first
#     t0 = time.perf_counter()
#     cached = await redis_client.get(cache_key)
#     t1 = time.perf_counter()

#     if cached:
#         print(f"  CACHE HIT: {(t1-t0)*1000:.2f}ms")
#         return json.loads(cached)

#     # 2. Cache miss — fetch from MongoDB
#     doc = await fetching_order({"orderId": order_id})
#     t2 = time.perf_counter()

#     if not doc:
#         raise HTTPException(status_code=404, detail="Order not found")

#     doc = dfsiteration(doc)

#     # 3. Store in Redis for next time (expires in 5 minutes)
#     await redis_client.set(cache_key, json.dumps(doc), ex=300)

#     print(f"  CACHE MISS | DB fetch: {(t2-t1)*1000:.2f}ms")
#     return doc



@app.get("/orders/fulldetails/{order_id}")
async def get_order(order_id: str):
    doc =  await get_full_order(order_id)
    print(doc)

    return doc




@app.get("/orders/{order_id}")
async def get_order(order_id: str):
    cache_key = f"order:{order_id}"
 
    # check when this order was last updated
    current_modified = await get_last_modified(order_id)
 
    # check if we already have it cached
    cached = await redis_client.get(cache_key)
 
    if cached:
        cached_data = cached
        
        if cached:
#         print(f"  CACHE HIT: {(t1-t0)*1000:.2f}ms")
#         return json.loads(cached)



#     # 2. Cache miss — fetch from MongoDB
#     doc = await fetching_order({"orderId": order_id})
#     t2 = time.perf_counter()

#     if not doc:
#         raise HTTPException(status_code=404, detail="Order not found")

#     doc = dfsiteration(doc)

#     # 3. Store in Redis for next time (expires in 5 minutes)
#     await redis_client.set(cache_key, json.dumps(doc), ex=300)

#     print(f"  CACHE MISS | DB fetch: {(t2-t1)*1000:.2f}ms")
#     return doc