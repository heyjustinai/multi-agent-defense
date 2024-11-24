import os
from dotenv import load_dotenv

def get_openai_api_key():
    """Get OpenAI API key from environment variables."""
    load_dotenv()  # Load environment variables from .env file
    return os.getenv('OPENAI_API_KEY')
