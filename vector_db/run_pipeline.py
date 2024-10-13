import json

from pipeline.news_api.extract import get_ai_news
from config import NEWS_API_ENDPOINT, NEWS_API_KEY

data = get_ai_news(NEWS_API_ENDPOINT, NEWS_API_KEY)


with open("result.json", mode="wt") as file:
    json.dump(data, file, indent=4)
