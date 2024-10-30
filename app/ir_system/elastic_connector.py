from elasticsearch import Elasticsearch


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
