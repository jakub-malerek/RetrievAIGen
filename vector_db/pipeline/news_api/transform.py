import sys
import os

sys.path.append(os.path.abspath("../../../models/huggingface"))  # noqa

from embedding import TextEmbedder

embedder = TextEmbedder()


def transform_data(news_data):
    """
    Transforms news data by generating embeddings for specified fields.

    Parameters:
        news_data (dict): The original news data dictionary.

    Returns:
        dict: Transformed data dictionary with additional vector fields.
    """

    transformed_data = {
        "author": news_data.get("author"),
        "content": news_data.get("content"),
        "description": news_data.get("description"),
        "publishedAt": news_data.get("publishedAt"),
        "source_name": news_data["source"].get("name") if news_data.get("source") else None,
        "title": news_data.get("title"),
        "url": news_data.get("url"),
    }

    if transformed_data["content"]:
        transformed_data["content_vector"] = embedder.get_embedding(transformed_data["content"])[0].tolist()
    if transformed_data["description"]:
        transformed_data["description_vector"] = embedder.get_embedding(transformed_data["description"])[0].tolist()
    if transformed_data["title"]:
        transformed_data["title_vector"] = embedder.get_embedding(transformed_data["title"])[0].tolist()

    return transformed_data
