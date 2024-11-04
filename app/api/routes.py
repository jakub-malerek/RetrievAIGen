from fastapi import APIRouter
from pydantic import BaseModel
from app.chatbot.bot import TechNewsChatbot
from app.ir_system.system import get_retriever
from app.config import ES_HOST, ES_PORT, ES_USER, ES_PASSWORD, OPENAI_API_KEY

# Initialize the router
router = APIRouter()

# Initialize the retriever and chatbot
retriever = get_retriever(ES_HOST, ES_PORT, ES_USER, ES_PASSWORD)
chatbot = TechNewsChatbot(api_key=OPENAI_API_KEY, retriever=retriever)

# Request and response models


class QuestionRequest(BaseModel):
    question: str


class AnswerResponse(BaseModel):
    answer: str

# Define the /ask route


@router.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    answer = chatbot.ask_question(request.question)
    return {"answer": answer}
