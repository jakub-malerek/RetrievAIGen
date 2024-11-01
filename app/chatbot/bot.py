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
        self.is_first_query = True  # Flag to track if IR has been used

        if retriever:
            self.setup_qa_chain()

    def setup_qa_chain(self):
        """Sets up the ConversationalRetrievalChain with a custom prompt."""
        if not self.retriever:
            raise ValueError("Retriever is not set. Please provide a retriever to set up the QA chain.")

        custom_prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="""You are a helpful assistant specialized in providing the latest technology news.

Instructions:
- Based on the provided news articles, create a response in a numbered list format.
- For each number:
    - Start with the number (e.g., "1.").
    - Provide a concise but thorough summary of a relevant topic from the articles.
    - Exhaust all the information you can infer from the article about that topic.
    - After the summary, politely invite the user to read more by providing the source URL.
- The conversation should be professional but kind.
- Ensure each point is clear and informative.

News Articles:
{context}

Question:
{question}

Answer:
"""
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

        if self.is_first_query:
            # Use information retrieval for the first query
            input_data = {
                "question": question,
                "chat_history": self.chat_history
            }

            # Get the response from the QA chain
            result = self.qa_chain(input_data)
            source_documents = result.get('source_documents', [])

            # Handle the case where no relevant documents were found
            if not source_documents:
                response = "I'm sorry, I couldn't find any information on that topic."
            else:
                # Prepare the context with content and URLs
                context_with_urls = ""
                for doc in source_documents:
                    content = doc.page_content
                    url = doc.metadata.get('url', 'URL not available')
                    context_with_urls += f"Article Content:\n{content}\nSource URL: {url}\n\n"

                # Create a new prompt including the context with URLs
                new_prompt = f"""
You are a helpful assistant specialized in providing the latest technology news.

Instructions:
- Based on the provided news articles, create a response in a numbered list format.
- For each number:
    - Start with the number (e.g., "1.").
    - Provide a concise but thorough summary of a relevant topic from the articles.
    - Exhaust all the information you can infer from the article about that topic.
    - After the summary, politely invite the user to read more by providing the source URL.
- The conversation should be professional but kind.
- Ensure each point is clear and informative.

News Articles:
{context_with_urls}

Question:
{question}

Answer:
"""

                # Generate the response using the LLM
                summary_response = self.llm(new_prompt)
                if hasattr(summary_response, 'content'):
                    response = summary_response.content.strip()
                else:
                    response = str(summary_response).strip()

            # Mark that the first query has been processed
            self.is_first_query = False
        else:
            # For subsequent queries, generate the response using chat history
            # Use a simplified prompt to continue the conversation
            conversation_context = "\n".join(
                f"User: {q}\nAssistant: {a}" for q, a in self.chat_history
            )
            new_prompt = f"""
Continue the conversation based on the following history:

{conversation_context}

User: {question}
Assistant:
"""

            # Generate the response using the LLM
            continuation_response = self.llm(new_prompt)
            if hasattr(continuation_response, 'content'):
                response = continuation_response.content.strip()
            else:
                response = str(continuation_response).strip()

        # Append the conversation to the chat history
        self.chat_history.append((question, response))

        return response
