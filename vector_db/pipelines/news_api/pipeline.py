from pipelines.news_api.extract import get_ai_news
from pipelines.news_api.transform import transform_data
from pipelines.news_api.load import load_document


def run_etl(news_endpoint: str, news_api_key: str, es_creds: dict, index_name: str):
    news_data = get_ai_news(endpoint=news_endpoint, api_key=news_api_key)
    transformed_data = [transform_data(news) for news in news_data]
    load_document(es_creds=es_creds, index_name=index_name, data=transformed_data)
