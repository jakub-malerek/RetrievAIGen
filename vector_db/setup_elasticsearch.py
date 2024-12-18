"""Module is used for database setup from python code. It creates index (table) in Elasticsearch with mapping (schema)."""
from pathlib import Path

from elasticsearch import Elasticsearch

from config import ES_HOST, ES_PORT, ES_USER, ES_PASSWORD, TECH_NEWS_INDEX
from db_management.index_management import create_index

es = Elasticsearch(
    hosts=[{"host": ES_HOST,
            "port": ES_PORT,
            "scheme": "https"}],
    basic_auth=(ES_USER, ES_PASSWORD),
    verify_certs=False
)


path_to_mapping = Path("db_management/schemas/news_articles_mapping.json")

create_index(elastic_instance=es, index_name=TECH_NEWS_INDEX, mapping=path_to_mapping)
