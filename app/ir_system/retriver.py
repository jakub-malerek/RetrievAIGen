from elasticsearch import Elasticsearch
from typing import List, Dict

from models.huggingface.embedding import TextEmbedder

embedder = TextEmbedder()


class InformationRetriever:
    def __init__(self, es_client: Elasticsearch, embedder=embedder, index_name="ai_news_01"):
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
            List[Dict]: List of search results.
        """
        # Step 1: Vectorize the query
        query_vector = self.vectorize_query(query)

        # Step 2: Define the search query with vector similarity and boosted keyword search
        search_query = {
            "size": top_k,
            "query": {
                "bool": {
                    "should": [
                        # Vector search for each vector field with equal weight
                        {
                            "script_score": {
                                "query": {
                                    "match_all": {}
                                },
                                "script": {
                                    "source": "cosineSimilarity(params.query_vector, 'content_vector') + 1.0",
                                    "params": {
                                        "query_vector": query_vector
                                    }
                                }
                            }
                        },
                        {
                            "script_score": {
                                "query": {
                                    "match_all": {}
                                },
                                "script": {
                                    "source": "cosineSimilarity(params.query_vector, 'description_vector') + 1.0",
                                    "params": {
                                        "query_vector": query_vector
                                    }
                                }
                            }
                        },
                        {
                            "script_score": {
                                "query": {
                                    "match_all": {}
                                },
                                "script": {
                                    "source": "cosineSimilarity(params.query_vector, 'title_vector') + 1.0",
                                    "params": {
                                        "query_vector": query_vector
                                    }
                                }
                            }
                        },
                        # Text-based keyword search with boosted fields
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

        # Step 3: Execute the search query
        response = self.es_client.search(index=self.index_name, body=search_query)

        # Step 4: Process and return results
        hits = response["hits"]["hits"]
        results = [
            {
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
