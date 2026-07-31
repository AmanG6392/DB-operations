import os
import asyncio
from dotenv import load_dotenv
from pymongo import AsyncMongoClient
from pymongo.server_api import ServerApi

load_dotenv()
uri = os.getenv("DATABASE_URL")

# Create a new client and connect to the server
client = AsyncMongoClient(uri, server_api=ServerApi('1'))



