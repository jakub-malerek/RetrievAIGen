from flask import Flask, request, jsonify
from flask_cors import CORS

from app.chatbot.bot import TechNewsChatbot
from app.ir_system.system import get_retriever
from app.config import ES_HOST, ES_PORT, ES_USER, ES_PASSWORD, OPENAI_API_KEY

app = Flask(__name__)
CORS(app)

retriever = get_retriever(ES_HOST, ES_PORT, ES_USER, ES_PASSWORD)
chatbot_instances = {}  # Store chatbot instances by session ID or user ID


def create_chatbot(persona="technical"):
    """Helper function to create a new chatbot with the specified persona."""
    return TechNewsChatbot(api_key=OPENAI_API_KEY, retriever=retriever, persona=persona)


@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.get_json()
    question = data.get('question')
    persona = data.get('persona', 'technical')
    new_session = data.get('new_session', False)

    if not question:
        return jsonify({"error": "Question is required"}), 400

    # Create a new chatbot instance if new session is requested or if no chatbot exists yet
    if new_session or 'chatbot' not in chatbot_instances:
        chatbot_instances['chatbot'] = create_chatbot(persona)

    # Use the existing chatbot instance to handle the question
    chatbot = chatbot_instances['chatbot']
    response = chatbot.ask_question(question)

    return jsonify({"response": response})
