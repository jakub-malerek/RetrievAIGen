import os
import yaml

from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env.db')
load_dotenv(dotenv_path=dotenv_path)

with open("config.yaml", mode="rt") as file:
    cfg = yaml.load(file, Loader=yaml.FullLoader)

# news api
NEWS_API_ENDPOINT = os.getenv("NEWS_API_ENDPOINT")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# elasticsearch
ES_HOST = os.getenv("ES_HOST")
ES_PORT = int(os.getenv("ES_PORT"))
ES_USER = os.getenv("ES_USER")
ES_PASSWORD = os.getenv("ES_PASSWORD")

# elastic specific
ES_AI_NEWS_INDEX = cfg["elasticsearch"]["indicies"]["ai_news"]
