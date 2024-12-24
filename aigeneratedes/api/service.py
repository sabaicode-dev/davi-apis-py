import requests
import os
from dotenv import load_dotenv

# Load environment variables
dotenv_path_dev = '.env'
load_dotenv(dotenv_path=dotenv_path_dev)

# Fetch the OpenAI API key from the environment variable
openai_api_key = os.getenv("OPENAI_API_KEY")
print("OpenAI API key:", openai_api_key)

def generate_description(columns: list, chart_type: str) -> str:
    """
    Generate a short and user-friendly description for visualizing the provided columns and chart type.
    This function interacts with the external service (e.g., OpenAI API) to get the description.
    """
    if not columns:
        return "No columns selected for visualization."

    # Create a dynamic description based on the selected columns
    columns_str = ", ".join(columns[:-1]) + f" and {columns[-1]}" if len(columns) > 1 else columns[0]
    
    # Modify prompt to ensure the model generates a concise response in English
    prompt = (
        f"Provide a short and clear description for visualizing data using the selected columns: {columns_str}. "
        f"The chart type will be {chart_type}. Keep it brief and easy to understand."
    )

    try:
        # API endpoint and headers
        url = "https://api.zukijourney.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {openai_api_key}",
            "Content-Type": "application/json"
        }

        # Payload for the API request
        payload = {
            "model": "gpt-3.5-turbo",  # Specify the model to use
            "messages": [{"role": "user", "content": prompt}]
        }

        # Make the API call
        response = requests.post(url, headers=headers, json=payload)

        # Check the response status
        if response.status_code == 200:
            response_data = response.json()

            # Check if 'choices' exist in the response and if it's non-empty
            if 'choices' in response_data and len(response_data['choices']) > 0:
                content = response_data['choices'][0].get('message', {}).get('content', '').strip()

                if content:
                    return content
                else:
                    return "Error generating description: No content returned from the model."
            else:
                return "Error generating description: No choices returned in the response."
        else:
            return f"Error in API call: {response.status_code} - {response.text}"

    except Exception as e:
        # Handle unexpected errors
        print(f"Error generating description: {e}")
        return "Error generating description. Please try again later."
