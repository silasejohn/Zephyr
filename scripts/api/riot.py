from dotenv import load_dotenv
import os

load_dotenv() # load environment variables from .env file

# Access the environment variables
RIOT_API_KEY = os.getenv('RIOT_API_KEY')
