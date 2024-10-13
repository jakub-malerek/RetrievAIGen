import requests


def get_ai_news(endpoint: str, api_key) -> list[dict]:
    params = {
        "q": "artificial intelligence OR ai",
        "from": "2024-10-05",
        "sortBy": "relevance",
        "language": "en"
    }
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    re = requests.get(endpoint, params=params, headers=headers)

    data = re.json()

    return data["articles"]
