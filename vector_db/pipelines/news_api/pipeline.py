"""This module orchestrates the ETL process for the News API data."""

from elasticsearch import Elasticsearch

from pipelines.news_api.extract import get_ai_news
from pipelines.news_api.transform import transform_data
from pipelines.news_api.load import bulk_load_documents


def run_etl(news_endpoint: str, news_api_key: str, es_instance: Elasticsearch, index_name: str):
    news_data = get_ai_news(endpoint=news_endpoint, api_key=news_api_key)
    transformed_data = [transform_data(news) for news in news_data]
    bulk_load_documents(es=es_instance, index_name=index_name, documents=transformed_data)


def run_etl_update(news_endpoint: str, news_api_key: str, es_instance: Elasticsearch, index_name: str):
    print(f"Clearing existing data from index '{index_name}'...")
    try:
        es_instance.delete_by_query(index=index_name, body={"query": {"match_all": {}}})
        print(f"Index '{index_name}' cleared successfully.")
    except Exception as e:
        print(f"Failed to clear index '{index_name}': {e}")
        return

    print("Re-ingesting fresh data...")
    run_etl(news_endpoint=news_endpoint, news_api_key=news_api_key, es_instance=es_instance, index_name=index_name)
    print(f"Index '{index_name}' updated with fresh data.")
