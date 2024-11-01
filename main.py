from app.ir_system.system import get_retriever
from app.chatbot.bot import TechNewsChatbot
from app.config import ES_HOST, ES_PORT, ES_USER, ES_PASSWORD, OPENAI_API_KEY

retriever = get_retriever(ES_HOST, ES_PORT, ES_USER, ES_PASSWORD)

chatbot = TechNewsChatbot(api_key=OPENAI_API_KEY, retriever=retriever)

question = "What's the latest news in artificial intelligence?"
answer = chatbot.ask_question(question)
print("Answer:", answer)

follow_up_question = "You are some sort of AI right?"
follow_up_answer = chatbot.ask_question(follow_up_question)
print("Follow-Up Answer:", follow_up_answer)

follow_up_question = "Do you remember first question I asked you?"
follow_up_answer = chatbot.ask_question(follow_up_question)
print("Follow-Up Answer:", follow_up_answer)
