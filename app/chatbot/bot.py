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
- Answer the question using **information from the news articles** provided.
- If you find **specific information**, provide a concise and accurate answer.
- If you don't find exact information but have **related details**, share a general answer based on that.
- If you couldn't find any relevant information, politely inform the user without mentioning "context" or technical terms.

{format_instructions}

News Articles:
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
            response = "I'm sorry, I couldn't find any information on that topic."
        else:
            related_info = self.extract_related_info(source_documents, question)
            if related_info:
                response = related_info
            else:
                response = "I'm sorry, I couldn't find any specific information on that topic."

        self.chat_history.append((question, response))

        return response

    def extract_related_info(self, documents, question):
        """
        Extracts related information from the documents.

        Parameters:
            documents (List[Document]): The documents to extract information from.
            question (str): The user's question.

        Returns:
            str: A summary of related information.
        """
        response_parts = []
        for doc in documents:
            content = doc.page_content
            metadata = doc.metadata
            url = metadata.get('url', '')
            source_name = metadata.get('source_name', 'Unknown Source')

            summary_prompt = f"""
You are an assistant helping to provide information based on the following news article:

Article Content:
{content}

Based on the article above, please provide a brief summary of any information related to the following question:

"{question}"

Your summary should be concise and mention any relevant details from the article.

Summary:
"""
            summary_response = self.llm(summary_prompt)
            if hasattr(summary_response, 'content'):
                summary_text = summary_response.content.strip()
            else:
                summary_text = str(summary_response).strip()

            if summary_text and "no relevant information" not in summary_text.lower():
                response_parts.append(f"{summary_text}\nFor more information, you can read here: {url}")
            else:
                continue

        if response_parts:
            return "\n\n".join(response_parts)
        else:
            return None
