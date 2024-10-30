from app.ir_system.elastic_connector import connect_to_es
from app.ir_system.retriver import InformationRetriever


def get_retriever(es_host: str, es_port: int, es_user: str, es_password: str) -> InformationRetriever:
    """
    Create an instance of the InformationRetriever class.

    Parameters:
        es_host (str): The Elasticsearch host.
        es_port (int): The Elasticsearch port.
        es_user (str): The Elasticsearch user.
        es_password (str): The Elasticsearch password.

    Returns:
        InformationRetriever: An instance of the InformationRetriever class.
    """
    es_client = connect_to_es(es_host, es_port, es_user, es_password)
    return InformationRetriever(es_client=es_client)
