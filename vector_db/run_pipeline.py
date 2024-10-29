from config import ES_HOST, ES_PORT, ES_USER, ES_PASSWORD, ES_AI_NEWS_INDEX, NEWS_API_ENDPOINT, NEWS_API_KEY
from pipelines.news_api.pipeline import run_etl
from utils.elasitc_utils import connect_to_es

es = connect_to_es(ES_HOST, ES_PORT, ES_USER, ES_PASSWORD)

run_etl(news_endpoint=NEWS_API_ENDPOINT, news_api_key=NEWS_API_KEY, es_instance=es, index_name=ES_AI_NEWS_INDEX)
