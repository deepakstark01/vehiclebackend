from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from load_dotenv import load_dotenv
import os
load_dotenv()
uri = os.getenv("MONGO_URI")
def get_db():
    client = MongoClient(uri, server_api=ServerApi('1'))
    db = client.vehicleapi
    return db
