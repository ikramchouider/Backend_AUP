import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import logging

load_dotenv()
MONGO_URI = os.getenv("DATA_BASE")

client = MongoClient(MONGO_URI, server_api=ServerApi('1'))

database = client["RAMY_APP"]

your_collection = database["TEST"]
Activity = database["Activity"]
Admin = database["Admin"]
Consumer = database["Consumer"]
Offer = database["Offer"]
Store = database["Store"]
Visit = database["Visit"]
Worker = database["Worker"]




