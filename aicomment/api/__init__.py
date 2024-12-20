from flask import Flask
from pymongo import MongoClient
from .urls import init_app

# MongoDB connection settings
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "myDatabase"  # Replace with your actual database name

def create_app():
    app = Flask(__name__)

    # MongoDB setup
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    app.db = db  # Attach the database to the app instance

    # Initialize URLs (routes)
    init_app(app)

    return app
