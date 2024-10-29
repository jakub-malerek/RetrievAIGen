from elasticsearch import Elasticsearch, RequestError, ConnectionError, TransportError


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
