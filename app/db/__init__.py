from pathlib import Path
import os
from pymongo import MongoClient, ASCENDING
from dotenv import load_dotenv


env_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

username1 = os.getenv("DB_USERNAME")
password2 = os.getenv("DB_PWD")
cluster3 = os.getenv("DB_CLUSTER")
username = os.environ.get("DB_USERNAME")
password = os.environ.get("DB_PWD")
cluster = os.environ.get("DB_CLUSTER")
client = MongoClient(f"mongodb+srv://{username}:{password}@{cluster}")

db = client["fleet-fortress"]
user_collection = db["users"]
register_codes = db["register_codes"]
register_codes.create_index([('expire_at', ASCENDING)], expireAfterSeconds=86400)
route_collection = db["routes"]
vehicle_collection = db["vehicles"]