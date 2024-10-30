"""This module implements the ElasticSearch utilities."""

from elasticsearch import Elasticsearch, RequestError, ConnectionError, TransportError, helpers


def connect_to_es(host: str, port: int, user: str, password: str) -> Elasticsearch:
    """
    Connect to an Elasticsearch instance.

    Parameters:
        host (str): The Elasticsearch host.
        port (int): The Elasticsearch port.
        user (str): The Elasticsearch user.
        password (str): The Elasticsearch password.

    Returns:
        Elasticsearch: The Elasticsearch client instance.
    """
    return Elasticsearch(
        hosts=[{"host": host, "port": port, "scheme": "https"}],
        basic_auth=(user, password),
        verify_certs=False
    )


def load_document(es: Elasticsearch, index_name: str, document: dict) -> bool:
    """
    Load a single document to the specified Elasticsearch index.

    Parameters:
        es (Elasticsearch): The Elasticsearch client instance.
        index_name (str): The name of the Elasticsearch index.
        document (dict): The document to be loaded.

    Returns:
        bool: True if the document was successfully indexed, False otherwise.
    """
    try:
        response = es.index(index=index_name, body=document)
        print(f"Document indexed successfully: {response['_id']}")
        return True
    except RequestError as e:
        print(f"Request error indexing document: {e}")
    except ConnectionError as e:
        print(f"Connection error indexing document: {e}")
    except TransportError as e:
        print(f"Transport error indexing document: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    return False


def bulk_load_documents(es: Elasticsearch, index_name: str, documents: list[dict]) -> bool:
    """
    Load multiple documents to the specified Elasticsearch index using bulk indexing.

    Parameters:
        es (Elasticsearch): The Elasticsearch client instance.
        index_name (str): The name of the Elasticsearch index.
        documents (list[dict]): List of documents to be loaded.

    Returns:
        bool: True if the documents were successfully indexed, False otherwise.
    """
    print("Preparing documents for bulk indexing...")
    actions = [
        {
            "_index": index_name,
            "_source": doc
        }
        for doc in documents
    ]

    try:
        helpers.bulk(es, actions)
        print(f"Successfully indexed {len(documents)} documents.")
        return True
    except RequestError as e:
        print(f"Request error during bulk indexing: {e}")
    except ConnectionError as e:
        print(f"Connection error during bulk indexing: {e}")
    except TransportError as e:
        print(f"Transport error during bulk indexing: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during bulk indexing: {e}")
    return False
