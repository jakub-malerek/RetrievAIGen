from app.ir_system.system import get_retriever
from app.chatbot.bot import TechNewsChatbot
from app.config import ES_HOST, ES_PORT, ES_USER, ES_PASSWORD, OPENAI_API_KEY

retriever = get_retriever(ES_HOST, ES_PORT, ES_USER, ES_PASSWORD)


chatbot = TechNewsChatbot(api_key=OPENAI_API_KEY, retriever=retriever)


question = "New from world of AI"
answer = chatbot.ask_question(question)
print("Answer:", answer)
