import os

from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env.db')
load_dotenv(dotenv_path=dotenv_path)

NEWS_API_ENDPOINT = os.getenv("NEWS_API_ENDPOINT")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
