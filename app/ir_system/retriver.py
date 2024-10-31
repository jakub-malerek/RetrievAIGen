import json
from typing import List, Dict
from pydantic import BaseModel, Field, root_validator
from elasticsearch import Elasticsearch
from langchain.schema import BaseRetriever, Document
from models.huggingface.embedding import TextEmbedder
from datetime import datetime


class InformationRetriever(BaseRetriever, BaseModel):
    es_client: Elasticsearch = Field(...)
    embedder: TextEmbedder = Field(default_factory=TextEmbedder)
    index_name: str = "tech_news_01"

    tags: List[str] = Field(default_factory=list)
    log_file: str = "retriever_log.json"  # Path to the log file

    class Config:
        arbitrary_types_allowed = True

    @root_validator(pre=True)
    def validate_es_client(cls, values):
        if not values.get("es_client"):
            raise ValueError("es_client is required and cannot be None.")
        return values

    def vectorize_query(self, query: str) -> List[float]:
        """Vectorizes the input query using the embedding model."""
        return self.embedder.get_embedding(query)[0]

    def log_documents(self, query: str, documents: List[Document]):
        """Logs the retrieved documents to a JSON file."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "documents": [
                {
                    "page_content": doc.page_content,
                    "metadata": doc.metadata
                }
                for doc in documents
            ]
        }

        try:
            # Append the log entry to the JSON file
            with open(self.log_file, "a") as file:
                file.write(json.dumps(log_entry, indent=4) + ",\n")
        except Exception as e:
            print(f"Failed to write log: {e}")

    def search(self, query: str, top_k: int = 5) -> List[Document]:
        """Performs a combined vector and keyword search on Elasticsearch and returns Document objects."""
        query_vector = self.vectorize_query(query)

        search_query = {
            "size": top_k,
            "query": {
                "bool": {
                    "should": [
                        {
                            "script_score": {
                                "query": {"exists": {"field": "content_vector"}},
                                "script": {
                                    "source": "cosineSimilarity(params.query_vector, 'content_vector') + 1.2",
                                    "params": {"query_vector": query_vector}
                                }
                            }
                        },
                        {
                            "multi_match": {
                                "query": query,
                                "fields": ["title^1.5", "description^1.2", "content"],
                                "type": "best_fields"
                            }
                        }
                    ]
                }
            }
        }

        response = self.es_client.search(index=self.index_name, body=search_query)
        hits = response["hits"]["hits"]

        # Merge relevant content parts for better context
        results = [
            Document(
                page_content=f"{hit['_source']['title']}\n\n{
                    hit['_source']['description']}\n\n{hit['_source']['content']}",
                metadata={
                    "author": hit["_source"].get("author", "Unknown"),
                    "publishedAt": hit["_source"].get("publishedAt"),
                    "source_name": hit["_source"].get("source_name"),
                    "url": hit["_source"].get("url"),
                    "topic": hit["_source"].get("topic"),
                    "score": hit["_score"]
                }
            )
            for hit in hits
        ]

        # Log the retrieved documents
        self.log_documents(query, results)

        return results

    def get_relevant_documents(self, query: str) -> List[Document]:
        """Returns relevant documents for a given query."""
        return self.search(query)

    async def aget_relevant_documents(self, query: str) -> List[Document]:
        """Asynchronously returns relevant documents for a given query."""
        return self.get_relevant_documents(query)
