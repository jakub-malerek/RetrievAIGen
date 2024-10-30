from elasticsearch import Elasticsearch
from typing import List, Dict
from models.huggingface.embedding import TextEmbedder

embedder = TextEmbedder()


class InformationRetriever:
    def __init__(self, es_client: Elasticsearch, embedder=embedder, index_name="tech_news_01"):
        self.es_client = es_client
        self.embedder = embedder
        self.index_name = index_name

    def vectorize_query(self, query: str) -> List[float]:
        """
        Vectorizes the input query using the embedding model.

        Parameters:
            query (str): The user input query.

        Returns:
            List[float]: The vector representation of the query.
        """
        return self.embedder.get_embedding(query)[0]

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Performs a combined vector and keyword search on ElasticSearch.

        Parameters:
            query (str): The user input query.
            top_k (int): Number of top results to return.

        Returns:
            List[Dict]: List of search results, including document _id for duplicate tracking.
        """
        query_vector = self.vectorize_query(query)

        search_query = {
            "size": top_k,
            "query": {
                "bool": {
                    "should": [
                        {
                            "script_score": {
                                "query": {"match_all": {}},
                                "script": {
                                    "source": "cosineSimilarity(params.query_vector, 'content_vector') + 1.0",
                                    "params": {"query_vector": query_vector}
                                }
                            }
                        },
                        {
                            "multi_match": {
                                "query": query,
                                "fields": ["title^2", "description^1.5", "content"],
                                "type": "best_fields"
                            }
                        }
                    ]
                }
            }
        }

        response = self.es_client.search(index=self.index_name, body=search_query)

        hits = response["hits"]["hits"]
        results = [
            {
                "_id": hit["_id"],
                "title": hit["_source"]["title"],
                "author": hit["_source"]["author"],
                "description": hit["_source"]["description"],
                "content": hit["_source"]["content"],
                "publishedAt": hit["_source"]["publishedAt"],
                "source_name": hit["_source"]["source_name"],
                "url": hit["_source"]["url"],
                "score": hit["_score"]
            }
            for hit in hits
        ]

        return results
