import os
from typing import List, Dict, Any, Optional
from pymongo import MongoClient
import openai
from dotenv import load_dotenv
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Load environment variables
load_dotenv()

# OpenAI configuration
openai.api_key = os.getenv('OPENAI_API_KEY')
openai.api_base = "https://api.zukijourney.com/v1"

# MongoDB setup
client = MongoClient(os.getenv("MONGODB_URI"))
db = client[os.getenv("MONGODB_DB", "hi")]

class MongoDBService:
    @staticmethod
    def get_collection_names() -> List[str]:
        """Get all collection names from the database."""
        return db.list_collection_names()

    @staticmethod
    def get_collection_schema(collection_name: str) -> Dict[str, Any]:
        """Generate a schema representation of the collection."""
        collection = db[collection_name]
        sample_docs = list(collection.aggregate([
            {"$sample": {"size": 5}},
            {"$project": {"_id": 0}}
        ]))
        
        schema = {}
        for doc in sample_docs:
            for key, value in doc.items():
                if key not in schema:
                    schema[key] = type(value).__name__
        return schema

class QueryService:
    @staticmethod
    def get_headers_from_mongo(collection_name: str) -> list:
        """Fetch headers from a specified MongoDB collection."""
        try:
            print(f"Attempting to fetch headers from collection: {collection_name}")
            collection = db[collection_name]
            sample_document = collection.find_one()
            if sample_document:
                print(f"Sample document found: {sample_document}")
                return list(sample_document.keys())
            else:
                print("No documents found in the collection.")
                raise ValueError("No documents found in the specified collection.") 
        except Exception as e:
            error_message = f"Error fetching headers from {collection_name}: {str(e)}"
            print(error_message)
            raise RuntimeError(error_message)
