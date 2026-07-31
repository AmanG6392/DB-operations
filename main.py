from fastapi import FastAPI


app = FastAPI()


@app.get("/")
async def document_fetch():
    return {"message":"Welcome to the jungle"}

