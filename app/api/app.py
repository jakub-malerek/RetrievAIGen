from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy.orm import Session
from app.chatbot.bot import TechNewsChatbot
from app.ir_system.system import get_retriever
from app.config import ES_HOST, ES_PORT, ES_USER, ES_PASSWORD, OPENAI_API_KEY
from app.api.database.db import SessionLocal
from app.api.database.models import ChatSession, Message

app = Flask(__name__)
CORS(app)

retriever = get_retriever(ES_HOST, ES_PORT, ES_USER, ES_PASSWORD)
chatbot_instances = {}


def create_chat_session(db: Session, persona: str) -> int:
    """Creates a new chat session with the specified persona."""
    new_session = ChatSession(persona=persona, closed=False)
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session.id


def add_message(db: Session, session_id: int, role: str, content: str):
    """Adds a message to an existing chat session."""
    new_message = Message(session_id=session_id, role=role, content=content)
    db.add(new_message)
    db.commit()


def close_session(db: Session, session_id: int):
    """Closes a chat session, making it read-only."""
    session = db.query(ChatSession).get(session_id)
    if session:
        session.closed = True
        db.commit()


@app.route('/start_session', methods=['POST'])
def start_session():
    data = request.get_json()
    persona = data.get('persona', 'technical')

    with SessionLocal() as db:
        previous_session_id = data.get('session_id')
        if previous_session_id:
            close_session(db, previous_session_id)
            chatbot_instances.pop(previous_session_id, None)

        session_id = create_chat_session(db, persona)
        chatbot_instances[session_id] = TechNewsChatbot(
            api_key=OPENAI_API_KEY, retriever=retriever, persona=persona
        )

    return jsonify({"session_id": session_id})


@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.get_json()
    question = data.get('question', "").strip()
    persona = data.get('persona', 'technical')
    session_id = data.get('session_id')

    if not session_id:
        return jsonify({"error": "Session ID is required."}), 400

    if not question:
        return jsonify({"error": "Question is required."}), 400

    with SessionLocal() as db:
        chat_session = db.query(ChatSession).get(session_id)
        if not chat_session or chat_session.closed:
            return jsonify({"error": "This session is closed or does not exist."}), 400

        chatbot = chatbot_instances.get(session_id)
        if chatbot is None:
            return jsonify({"error": "Chatbot instance not found for this session."}), 500
        response = chatbot.ask_question(question)
        add_message(db, session_id, "user", question)
        add_message(db, session_id, "assistant", response)

    return jsonify({"response": response, "session_id": session_id})


@app.route('/history/<int:session_id>', methods=['GET'])
def get_history(session_id):
    with SessionLocal() as db:
        history = db.query(Message).filter(Message.session_id == session_id).all()
        return jsonify([
            {"role": msg.role, "content": msg.content} for msg in history
        ])


@app.route('/close/<int:session_id>', methods=['POST'])
def close_chat(session_id):
    with SessionLocal() as db:
        close_session(db, session_id)
        chatbot_instances.pop(session_id, None)
        return jsonify({"message": "Session closed."})


if __name__ == '__main__':
    app.run(port=8000, debug=True)
