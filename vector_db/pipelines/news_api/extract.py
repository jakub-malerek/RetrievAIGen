"""This module implements the data extraction logic for the News API."""
import requests
from datetime import datetime, timedelta


def get_ai_news(endpoint: str, api_key: str) -> list[dict]:
    """Extract AI news data from the News API for the past week."""

    one_week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

    params = {
        "q": "artificial intelligence OR ai",
        "from": one_week_ago,
        "sortBy": "relevance",
        "language": "en"
    }
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    try:
        print(f"Requesting AI news data from News API starting from {one_week_ago}...")
        response = requests.get(endpoint, params=params, headers=headers)
        response.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return []
    except requests.exceptions.ConnectionError:
        print("Error: Unable to connect to the News API.")
        return []
    except requests.exceptions.Timeout:
        print("Error: The request to News API timed out.")
        return []
    except requests.exceptions.RequestException as err:
        print(f"An error occurred: {err}")
        return []

    try:
        data = response.json()
        articles = data.get("articles", [])
        print(f"Successfully retrieved {len(articles)} articles.")
        return articles
    except ValueError:
        print("Error: Failed to parse JSON response.")
        return []
