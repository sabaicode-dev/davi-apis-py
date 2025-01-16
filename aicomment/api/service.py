# import os
# from typing import List, Dict, Any, Optional
# from pymongo import MongoClient
# import openai
# from dotenv import load_dotenv
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# import ast
# # Load environment variables
# load_dotenv()

# # OpenAI configuration
# openai.api_key = os.getenv('OPENAI_API_KEY')
# openai.api_base = "https://api.zukijourney.com/v1"

# # MongoDB setup
# client = MongoClient(os.getenv("MONGODB_URI"))
# db = client[os.getenv("MONGODB_DB", "hi")]

# import logging
# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# def validate_query(query: Dict) -> Dict:
#     """
#     Validate the query to ensure it is compatible with the `find` method.
#     Removes top-level operators like `$match` and ensures the query is a valid dictionary.
#     """
#     if isinstance(query, dict):
#         # Remove top-level operators like $match
#         if "$match" in query:
#             return query["$match"]
#     return query

# class MongoDBService:
#     @staticmethod
#     def get_collection_names() -> List[str]:
#         """Get all collection names from the database."""
#         try:
#             return db.list_collection_names()
#         except Exception as e:
#             logger.error(f"Error fetching collection names: {e}")
#             raise

#     @staticmethod
#     def get_collection_schema(collection_name: str) -> Dict[str, Any]:
#         """Generate a schema representation of the collection."""
#         try:
#             collection = db[collection_name]
#             sample_docs = list(collection.aggregate([
#                 {"$sample": {"size": 5}},
#                 {"$project": {"_id": 0}}
#             ]))
            
#             schema = {}
#             for doc in sample_docs:
#                 for key, value in doc.items():
#                     if key not in schema:
#                         schema[key] = type(value).__name__
#             return schema
#         except Exception as e:
#             logger.error(f"Error generating schema for collection {collection_name}: {e}")
#             raise

# class QueryService:
#     @staticmethod
#     def generate_mongo_query_from_prompt(prompt: str, collection_name: str, schema: Dict) -> Dict:
#         """Generate MongoDB query from natural language prompt using OpenAI."""
#         try:
#             # Construct the message for OpenAI
#             system_message = f"""
#             You are a MongoDB query generator. Given the collection schema: {schema}
#             Generate a MongoDB query based on the user's prompt.
#             Return only the query object in valid Python dictionary format.
#             The query should be compatible with the `find` method, not an aggregation pipeline.
#             Do not include top-level operators like `$match`.
#             """
            
#             response = openai.ChatCompletion.create(
#                 model="gpt-3.5-turbo",  # Use gpt-3.5-turbo instead of gpt-4
#                 messages=[
#                     {"role": "system", "content": system_message},
#                     {"role": "user", "content": prompt}
#                 ],
#                 temperature=0.7
#             )
            
#             # Extract and safely parse the query string to convert it to a dictionary
#             query_str = response.choices[0].message.content.strip()
#             try:
#                 # Use ast.literal_eval for safer parsing
#                 query_dict = ast.literal_eval(query_str)
#                 # Validate the query
#                 query_dict = validate_query(query_dict)
#                 return query_dict
#             except (ValueError, SyntaxError) as e:
#                 logger.error(f"Error parsing query string: {e}")
#                 return {"$match": {}} # Return empty match if query generation fails
                
#         except Exception as e:
#             logger.error(f"Error generating MongoDB query: {e}")
#             return {"error": str(e)}

#     @staticmethod
#     def execute_mongo_query(collection_name: str, query: Dict) -> List[Dict]:
#         """Execute the generated MongoDB query."""
#         try:
#             collection = db[collection_name]
#             results = list(collection.find(query, {'_id': 0}))
#             return results
#         except Exception as e:
#             logger.error(f"Error executing query: {e}")
#             raise RuntimeError(f"Error executing query: {str(e)}")


import os
from typing import List, Dict, Any
from pymongo import MongoClient
import openai
from dotenv import load_dotenv
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import ast
import logging

# Load environment variables
load_dotenv()

# OpenAI configuration
openai.api_key = os.getenv('OPENAI_API_KEY')
openai.api_base = "https://api.zukijourney.com/v1"

# MongoDB setup
client = MongoClient(os.getenv("MONGODB_URI"))
db = client[os.getenv("MONGODB_DB", "hi")]

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_query(query: Dict) -> Dict:
    """
    Validate the query to ensure it is compatible with the `find` method.
    Removes top-level operators like `$match` and ensures the query is a valid dictionary.
    """
    if isinstance(query, dict):
        # Remove top-level operators like $match
        if "$match" in query:
            return query["$match"]
    return query

class MongoDBService:
    @staticmethod
    def get_collection_names() -> List[str]:
        """Get all collection names from the database."""
        try:
            return db.list_collection_names()
        except Exception as e:
            logger.error(f"Error fetching collection names: {e}")
            raise

    @staticmethod
    def get_collection_schema(collection_name: str) -> Dict[str, Any]:
        """Generate a schema representation of the collection."""
        try:
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
        except Exception as e:
            logger.error(f"Error generating schema for collection {collection_name}: {e}")
            raise

class QueryService:
    @staticmethod
    def generate_mongo_query_from_prompt(prompt: str, collection_name: str, schema: Dict) -> Dict:
        """Generate MongoDB query from natural language prompt using OpenAI."""
        try:
            # Construct the message for OpenAI
            system_message = f"""
            You are a MongoDB query generator. Given the collection schema: {schema}
            Generate a MongoDB query based on the user's prompt.
            Return only the query object in valid Python dictionary format.
            The query should be compatible with the `find` method, not an aggregation pipeline.
            Do not include top-level operators like `$match`.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # Use gpt-3.5-turbo instead of gpt-4
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            # Extract and safely parse the query string to convert it to a dictionary
            query_str = response.choices[0].message.content.strip()
            try:
                # Use ast.literal_eval for safer parsing
                query_dict = ast.literal_eval(query_str)
                # Validate the query
                query_dict = validate_query(query_dict)
                return query_dict
            except (ValueError, SyntaxError) as e:
                logger.error(f"Error parsing query string: {e}")
                return {"status": "active"}  # Fallback to a simple query
                
        except Exception as e:
            logger.error(f"Error generating MongoDB query: {e}")
            return {"error": str(e)}