# bot.py

from langchain.chains import ConversationalRetrievalChain
try:
    from langchain_openai import ChatOpenAI
except ImportError:
    from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate


class TechNewsChatbot:
    def __init__(self, api_key: str, retriever=None):
        """
        Initializes the Tech News chatbot.

        Parameters:
            api_key (str): The API key for OpenAI.
            retriever: The information retriever instance (optional).
        """
        self.llm = ChatOpenAI(api_key=api_key, model_name="gpt-4")
        self.retriever = retriever
        self.qa_chain = None
        self.chat_history = []
        if retriever:
            self.setup_qa_chain()

    def setup_qa_chain(self):
        """Sets up the ConversationalRetrievalChain if a retriever is provided."""
        if not self.retriever:
            raise ValueError("Retriever is not set. Please provide a retriever to set up the QA chain.")
        self.qa_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.retriever
        )

    def ask_question(self, question: str) -> str:
        """
        Asks a question and returns the answer.

        Parameters:
            question (str): The question to ask.

        Returns:
            str: The answer from the chatbot.
        """
        if not self.qa_chain:
            raise ValueError("QA chain is not set up. Please provide a retriever and call setup_qa_chain().")

        input_data = {
            "question": question,
            "chat_history": self.chat_history
        }

        response = self.qa_chain.invoke(input_data)

        self.chat_history.append((question, response))

        return response
