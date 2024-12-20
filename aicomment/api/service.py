import requests
import os
import openai
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables
dotenv_path_dev = '.env'
load_dotenv(dotenv_path=dotenv_path_dev)

# Fetch the OpenAI API key from the environment variable
openai_api_key = os.getenv("OPENAI_API_KEY")

# Set the OpenAI API key for authentication
openai.api_key = openai_api_key

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")  # MongoDB connection
db = client["myDatabase"]  # Replace with your actual MongoDB database name


def get_headers_from_mongo(collection_name: str) -> list:
    """
    Automatically fetch the headers (field names) from the specified MongoDB collection.
    """
    collection = db[collection_name]
    sample_document = collection.find_one()  # Fetch one document to get the keys (headers)
    
    if sample_document:
        return list(sample_document.keys())  # Return the field names (keys) as headers
    else:
        return []  # Return an empty list if no document is found


def generate_mongo_query_from_prompt(prompt: str, headers: list) -> str:
    """
    Generate a MongoDB query using the provided prompt and headers.
    This function interacts with the OpenAI API to generate a MongoDB query.
    """
    if not prompt or not headers:
        return "Prompt and headers are required to generate a query."

    # Create a dynamic description based on the provided prompt and headers
    headers_str = ", ".join(headers[:-1]) + f" and {headers[-1]}" if len(headers) > 1 else headers[0]
    
    # Modify prompt to ensure the model generates a valid MongoDB query
    prompt_text = (
        f"Generate a MongoDB query to select the following fields: {headers_str}. "
        f"Based on this prompt: {prompt}. Return the query in MongoDB syntax."
    )

    try:
        # OpenAI API call to generate the query
        response = openai.Completion.create(
            model="gpt-3.5-turbo",  # Specify the model (can be replaced with other models like GPT-4)
            messages=[
                {"role": "system", "content": 
                    """You are an AI assistant that converts user prompts into valid MongoDB query instructions.
                    Instructions must include:
                    - operation: MongoDB method (e.g., find, findOne, etc.)
                    - query: The filter object
                    - options: Any additional options like sort, limit, select, skip, etc.
                    The schema for reference is:
                    - name: String
                    - price: Number
                    - category: String
                    Return only the instructions in JSON format."""},
                {"role": "user", "content": prompt_text}
            ],
            max_tokens=150  # Limit the number of tokens in the response
        )

        # Check if we received a valid response from the model
        if response and 'choices' in response and len(response['choices']) > 0:
            query_text = response['choices'][0]['message']['content'].strip()

            if not query_text:
                return "Error: No query returned from AI."

            # Clean and parse the generated query from the AI response
            clean_string = query_text.replace("```json", "").replace("```", "").strip()
            ai_generated_instructions = eval(clean_string)  # Convert the string to a Python dictionary

            # Check if the AI generated valid instructions
            if 'operation' not in ai_generated_instructions:
                return "Error: Invalid AI-generated instructions."

            return ai_generated_instructions
        else:
            return "Error generating query from AI."

    except Exception as e:
        print(f"Error with OpenAI API: {e}")
        return f"Error: {str(e)}"


def execute_mongo_query(query: dict):
    """
    Executes a MongoDB query and returns the result.
    """
    try:
        # Extract the operation and query from the instructions
        operation = query.get('operation', 'find')
        mongo_query = query.get('query', {})
        options = query.get('options', {})

        # Get the collection to query from
        collection = db["products"]  # Replace with your collection name

        # Use the appropriate MongoDB method based on the operation
        if operation == 'find':
            results = collection.find(mongo_query, **options)
        elif operation == 'findOne':
            results = collection.find_one(mongo_query)
        else:
            results = []

        # Return the results as a list (for find, we convert the cursor to a list)
        result_list = [result for result in results] if isinstance(results, list) else results
        return result_list

    except Exception as e:
        print(f"Error executing query: {e}")
        return f"Error executing query: {str(e)}"


def generate_and_execute_query(prompt: str, collection_name: str):
    """
    Combines the AI query generation and MongoDB query execution.
    This function generates a query based on the prompt and headers, and then executes it on MongoDB.
    """
    # Step 1: Get the headers from MongoDB
    headers = get_headers_from_mongo(collection_name)

    if not headers:
        return f"Error: No headers found in the collection {collection_name}."

    # Step 2: Generate the MongoDB query based on the prompt and headers
    query = generate_mongo_query_from_prompt(prompt, headers)

    # If there was an error generating the query, return the error
    if query.startswith("Error"):
        return query

    # Step 3: Execute the generated query on MongoDB
    results = execute_mongo_query(query)

    return results
