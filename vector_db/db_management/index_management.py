import json
from pathlib import Path

from elasticsearch import Elasticsearch


def create_index(elastic_instance: Elasticsearch, index_name: str, mapping: dict | Path) -> None:
    if not elastic_instance.indices.exists(index=index_name):

        if isinstance(mapping, Path):
            with open(mapping, mode="rt", encoding="utf-8") as file:
                mapping = json.load(file)

        elastic_instance.indices.create(index=index_name, body=mapping)


def update_mapping(elastic_instance: Elasticsearch, index_name: str, mapping: dict | Path) -> None:

    if isinstance(mapping, Path):
        with open(mapping, mode="rt") as file:
            mapping = json.load(file)

    elastic_instance.indices.put_mapping(index=index_name, body=mapping)
