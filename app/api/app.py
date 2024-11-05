from flask import Flask, request, jsonify
from flask_cors import CORS

from app.chatbot.bot import TechNewsChatbot
from app.ir_system.system import get_retriever
from app.config import ES_HOST, ES_PORT, ES_USER, ES_PASSWORD, OPENAI_API_KEY

app = Flask(__name__)
CORS(app)

retriever = get_retriever(ES_HOST, ES_PORT, ES_USER, ES_PASSWORD)
chatbot = TechNewsChatbot(api_key=OPENAI_API_KEY, retriever=retriever)


@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.get_json()
    question = data.get('question')
    if not question:
        return jsonify({"error": "Question is required"}), 400

    response = chatbot.ask_question(question)
    return jsonify({"response": response})
