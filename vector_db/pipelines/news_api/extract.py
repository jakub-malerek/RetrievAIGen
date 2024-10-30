"""This module implements the data extraction logic for the News API."""
import requests
import time
from datetime import datetime, timedelta

# List of tech topics to retrieve news for
TOPICS = [
    "artificial intelligence OR ai",
    "blockchain OR cryptocurrency",
    "cybersecurity OR hacking",
    "cloud computing",
    "quantum computing",
    "data science OR big data",
    "5G OR network technology",
    "augmented reality OR virtual reality OR AR OR VR",
    "internet of things OR IoT",
    "green technology OR renewable energy",
    "digital privacy OR data protection",
    "fintech OR financial technology",
    "e-commerce",
    "gaming OR video games",
    "autonomous vehicles OR self-driving cars",
    "wearable technology OR wearables",
    "software development",
    "biotechnology OR biotech",
    "space technology OR space exploration",
    "educational technology OR EdTech"
]

one_week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')


def get_tech_news(endpoint: str, api_key: str, topics: list[str] = TOPICS, delay: int = 2) -> list[dict]:
    """
    Extracts tech news data from the News API for each specified topic in the past week,
    with deduplication based on article URLs.
    """
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    all_articles = []
    seen_urls = set()  # Set to track seen URLs for deduplication

    for topic in topics:
        print(f"Requesting news data for topic '{topic}' from News API starting from {one_week_ago}...")

        params = {
            "q": topic,
            "from": one_week_ago,
            "sortBy": "relevance",
            "language": "en",
            "pageSize": 100,
            "page": 1
        }

        try:
            response = requests.get(endpoint, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            articles = data.get("articles", [])
            print(f"Retrieved {len(articles)} articles for topic '{topic}'.")

            for article in articles:
                if article["url"] not in seen_urls:
                    seen_urls.add(article["url"])
                    article["topic"] = topic
                    all_articles.append(article)
                else:
                    print(f"Duplicate article detected and skipped: {article['title']}")

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred while fetching topic '{topic}': {http_err}")
        except requests.exceptions.ConnectionError:
            print(f"Error: Unable to connect to the News API for topic '{topic}'.")
        except requests.exceptions.Timeout:
            print(f"Error: The request to News API timed out for topic '{topic}'.")
        except requests.exceptions.RequestException as err:
            print(f"An error occurred while fetching topic '{topic}': {err}")
        except ValueError:
            print(f"Error: Failed to parse JSON response for topic '{topic}'.")

        # Delay to avoid hitting the API rate limit
        time.sleep(delay)

    print(f"Total articles retrieved after deduplication: {len(all_articles)}")
    return all_articles
