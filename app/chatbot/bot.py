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
        """Sets up the ConversationalRetrievalChain with a custom prompt."""
        if not self.retriever:
            raise ValueError("Retriever is not set. Please provide a retriever to set up the QA chain.")

        custom_prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="""
You are a helpful assistant specialized in providing the latest technology news.

Instructions:
- Use the **provided context** to answer the question.
- If you find **specific information** in the context, provide a concise and accurate answer using that information.
- If the context doesn't contain the specific answer but includes **related information**, provide a general answer based on that.
- If the context doesn't contain relevant information, politely inform the user that you couldn't find information on that subject.

{format_instructions}

Context:
{context}

Question:
{question}

Answer:
""",
            partial_variables={"format_instructions": ""}
        )

        self.qa_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.retriever,
            return_source_documents=True,
            max_tokens_limit=3500,
            combine_docs_chain_kwargs={'prompt': custom_prompt}
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

        result = self.qa_chain(input_data)
        response = result['answer']
        source_documents = result.get('source_documents', [])

        if not source_documents:
            response = "I'm sorry, I couldn't find any information on that subject."
        else:
            if "could not find specific information" in response.lower() or "does not provide specific information" in response.lower():
                response = f"While I couldn't find exact information on your question, here's what I found:\n{response}"

        self.chat_history.append((question, response))

        return response
