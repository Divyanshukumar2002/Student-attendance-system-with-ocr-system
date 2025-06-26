from flask_pymongo import PyMongo
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["ocr_app_db"]  # Database Name
data_collection = db["extracted_data"]  # Collection Name


mongo = None

def init_db(app):
    global mongo
    app.config["MONGO_URI"] = "mongodb://localhost:27017/ocr_app_db"
    
    mongo = PyMongo(app)
    print(f"pymango {mongo}")
    
