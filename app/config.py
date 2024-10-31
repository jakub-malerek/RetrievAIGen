from dotenv import load_dotenv
import os
from pathlib import Path

# Automatically load the .env file
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Elasticsearch setup
ES_HOST = os.getenv("ES_HOST")
ES_PORT = int(os.getenv("ES_PORT"))
ES_USER = os.getenv("ES_USER")
ES_PASSWORD = os.getenv("ES_PASSWORD")

# Hugging Face setup
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
HF_LLM_MODEL = os.getenv("HF_LLM_MODEL")
HF_EMBEDDING_MODEL = os.getenv("HF_EMBEDDING_MODEL")

# OpenAI setup
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
