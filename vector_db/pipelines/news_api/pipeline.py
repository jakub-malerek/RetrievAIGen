"""This module orchestrates the ETL process for the News API data."""

from pipelines.news_api.extract import get_ai_news
from pipelines.news_api.transform import transform_data
from pipelines.news_api.load import bulk_load_documents


def run_etl(news_endpoint: str, news_api_key: str, es_instance: str, index_name: str):
    news_data = get_ai_news(endpoint=news_endpoint, api_key=news_api_key)
    transformed_data = [transform_data(news) for news in news_data]
    bulk_load_documents(es=es_instance, index_name=index_name, documents=transformed_data)
