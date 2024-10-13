from pathlib import Path

from elasticsearch import Elasticsearch

from config import ES_HOST, ES_PORT, ES_USER, ES_PASSWORD, ES_AI_NEWS_INDEX
from db_management.index_management import create_index

es = Elasticsearch(
    hosts=[{"host": ES_HOST,
            "port": ES_PORT,
            "scheme": "https"}],
    basic_auth=(ES_USER, ES_PASSWORD),
    verify_certs=False
)


path_to_mapping = Path("db_management/schemas/news_articles_mapping.json")

create_index(elastic_instance=es, index_name=ES_AI_NEWS_INDEX, mapping=path_to_mapping)
