import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import logging

load_dotenv()
MONGO_URI = os.getenv("DATA_BASE")

client = AsyncIOMotorClient(MONGO_URI)

database = client["RAMY_APP"]

your_collection = database["TEST"]
Activity = database["Activity"]
Admin = database["Admin"]
Consumer = database["Consumer"]
Offer = database["Offer"]
Store = database["Store"]
Visit = database["Visit"]
Worker = database["Worker"]




