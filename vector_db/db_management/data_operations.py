import json
from pathlib import Path

import ftfy
from elasticsearch import Elasticsearch, helpers

from index_management import create_index


def bulk_index(elastic_instance: Elasticsearch, data: list[dict] | Path, index_name: str, start_id: int = 0) -> None:
    def preprocess_to_bulk(data: list[dict], index_name: str, start_id: int) -> list[dict]:
        if isinstance(data, Path):
            with open(data, mode="rt", encoding="utf-8") as file:
                raw_data = file.read()
                fixed_data = ftfy.fix_text(raw_data)
                data = json.loads(fixed_data)

        docs = []
        for n, doc in enumerate(data):
            preprocessed_doc = {
                "_index": index_name,
                "_id": start_id + n,
                "_source": doc
            }
            docs.append(preprocessed_doc)
        return docs

    processed_data = preprocess_to_bulk(data=data, index_name=index_name, start_id=start_id)

    helpers.bulk(elastic_instance, processed_data)


def delete_all_documents(elastic_instance: Elasticsearch, index_name: str) -> None:
    full_delete_query = {
        "match_all": {}
    }

    elastic_instance.delete_by_query(index=index_name, query=full_delete_query)


def data_migration(elasitc_instance: Elasticsearch,
                   source_index: str,
                   target_index: str,
                   mapping: dict | Path = None) -> None:

    if mapping:
        create_index(elastic_instance=elasitc_instance, index_name=target_index, mapping=mapping)

    elasitc_instance.reindex(source={"index": source_index}, dest={"index": target_index})
