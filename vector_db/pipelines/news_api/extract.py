"""This module implements the data extraction logic for the News API."""
import requests
import time
from datetime import datetime, timedelta

# List of tech topics to retrieve news for
TOPICS = [
    "artificial intelligence OR ai",
    "blockchain OR cryptocurrency",
    "cybersecurity OR hacking",
    "cloud computing OR edge computing",
    "quantum computing OR quantum cryptography",
    "data science OR big data",
    "5G OR network technology",
    "augmented reality OR virtual reality",
    "internet of things OR IoT",
    "green technology OR renewable energy",
    "digital privacy OR data protection",
    "fintech OR digital banking",
    "e-commerce OR digital marketplaces",
    "gaming OR esports",
    "autonomous vehicles OR self-driving cars",
    "wearable technology OR fitness tech",
    "software development OR coding",
    "biotechnology OR genetic engineering",
    "space technology OR space exploration",
    "educational technology OR online learning",
    "robotics OR automation",
    "digital marketing OR social media",
    "nanotechnology OR nanoengineering",
    "smart cities OR urban tech",
    "healthtech OR telemedicine",
    "supply chain technology OR logistics tech",
    "3D printing OR additive manufacturing",
    "drones OR unmanned aerial vehicles",
    "natural language processing OR NLP",
    "predictive analytics OR business intelligence",
    "smart home OR home automation",
    "Tesla OR electric vehicles",
    "Apple OR iPhone",
    "Google OR Alphabet",
    "Microsoft OR Windows",
    "Amazon OR e-commerce",
    "Meta OR Facebook",
    "Samsung OR Galaxy",
    "Nvidia OR GPUs",
    "Intel OR processors",
    "IBM OR mainframe",
    "Oracle OR database",
    "Zoom OR video conferencing",
    "Salesforce OR CRM",
    "TikTok OR ByteDance",
    "Spotify OR music streaming",
    "Netflix OR streaming services",
    "Adobe OR creative software",
    "Snapchat OR social media",
    "Uber OR ride-sharing",
    "Lyft OR ride-hailing",
    "PayPal OR online payments"
]


ONE_WEEK_AGO = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')


def get_tech_news(endpoint: str, api_key: str, from_date: str, to_date: str, topics: list[str] = TOPICS,  delay: int = 2) -> list[dict]:
    """
    Extracts tech news data from the News API for each specified topic in the past week,
    with deduplication based on article URLs.
    """
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    all_articles = []
    seen_urls = set()

    for topic in topics:
        print(f"Requesting news data for topic '{topic}' from News API starting from {from_date}...")

        params = {
            "q": topic,
            "from": from_date,
            "to": to_date,
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
                    print(f"Duplicate article detected and skipped: {article['title']}, url: {article['url']}")

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

        time.sleep(delay)

    print(f"Total articles retrieved after deduplication: {len(all_articles)}")
    return all_articles


def iterate_days(one_week_ago: str = ONE_WEEK_AGO) -> list[tuple[str, str]]:
    dates = []
    start_date = datetime.strptime(one_week_ago, '%Y-%m-%d')
    for i in range(7):
        from_date = (start_date + timedelta(days=i)).strftime('%Y-%m-%d')
        to_date = (start_date + timedelta(days=i+1) - timedelta(seconds=1)).strftime('%Y-%m-%d')
        dates.append((from_date, to_date))
    return dates


def recent_week_etl(endpoint: str, api_key: str, delay: int = 2) -> list[dict]:
    """
    Extracts tech news data from the News API for the past week for each topic.
    """
    all_articles = []
    date_ranges = iterate_days()

    for from_date, to_date in date_ranges:
        articles = get_tech_news(endpoint, api_key, from_date, to_date, delay=delay)
        all_articles.extend(articles)

    return all_articles
