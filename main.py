import json
from app.ir_system.system import get_retriever
from app.config import ES_HOST, ES_PORT, ES_USER, ES_PASSWORD

retriever = get_retriever(ES_HOST, ES_PORT, ES_USER, ES_PASSWORD)

prompt = "Any updates from world of AI?"

results = retriever.search(prompt, top_k=5)

with open("results.json", mode="wt") as file:
    json.dump(results, file, indent=4)
