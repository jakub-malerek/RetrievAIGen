from typing import List, Dict
from langchain.chat_models import ChatOpenAI
from langchain.schema import Document
from app.chatbot.intent_classifier import RunInformationRetrievalClassifier


class TechNewsChatbot:
    def __init__(self, api_key: str, retriever=None):
        """
        Initializes the Tech News chatbot.

        Parameters:
            api_key (str): The API key for OpenAI.
            retriever: The information retriever instance (optional).
        """
        self.llm = ChatOpenAI(api_key=api_key, model_name="gpt-4", temperature=0.2)
        self.retriever = retriever
        self.chat_history = []
        self.ir_classifier = RunInformationRetrievalClassifier()

    def ask_question(self, question: str) -> str:
        """
        Processes the user's question and generates an appropriate response.

        Parameters:
            question (str): The user's question.

        Returns:
            str: The chatbot's response.
        """
        # Update chat history with the user's question
        self.chat_history.append({"role": "user", "content": question})

        # Determine if IR is needed
        use_ir = self.ir_classifier.classify(question)
        print(f"Classifier returned: {use_ir}")

        if use_ir == "yes" and self.retriever is not None:
            response = self.handle_ir_question(question)
        else:
            response = self.handle_general_question(question)

        # Update chat history with the assistant's response
        self.chat_history.append({"role": "assistant", "content": response})

        return response

    def handle_ir_question(self, question: str) -> str:
        """
        Handles questions that require information retrieval.

        Parameters:
            question (str): The user's question.

        Returns:
            str: The chatbot's response.
        """
        # Retrieve documents
        retrieved_docs = self.retriever.get_relevant_documents(question)

        # Determine relevance of documents
        relevant_docs = self.filter_relevant_documents(question, retrieved_docs)

        if not relevant_docs:
            # No relevant documents found
            return self.handle_no_relevant_info(question)
        else:
            # Generate response using relevant documents
            return self.generate_response_with_docs(question, relevant_docs)

    def filter_relevant_documents(self, question: str, documents: List[Document]) -> List[Document]:
        """
        Filters documents to find those relevant to the question.

        Parameters:
            question (str): The user's question.
            documents (List[Document]): Retrieved documents.

        Returns:
            List[Document]: Relevant documents.
        """
        relevant_docs = []
        for doc in documents:
            # Check relevance using the LLM
            prompt = f"""
You are an AI assistant helping to determine document relevance.

Question: {question}

Document Content:
{doc.page_content}

Is this document relevant to answering the question? Respond with 'yes' or 'no'.
"""
            relevance_response = self.llm.invoke(prompt).content.strip().lower()
            if 'yes' in relevance_response:
                relevant_docs.append(doc)

        return relevant_docs

    def generate_response_with_docs(self, question: str, documents: List[Document]) -> str:
        """
        Generates a response using the relevant documents.

        Parameters:
            question (str): The user's question.
            documents (List[Document]): Relevant documents.

        Returns:
            str: The chatbot's response.
        """
        # Prepare conversation context
        conversation = self.format_chat_history()

        # Prepare context for the LLM
        formatted_docs = []
        for idx, doc in enumerate(documents, start=1):
            url = doc.metadata.get('url', None)
            if url:
                formatted_docs.append(f"{idx}. {doc.page_content}\nSource URL: {url}")
            else:
                formatted_docs.append(f"{idx}. {doc.page_content}\nSource URL: URL not available")

        context = "\n\n".join(formatted_docs)

        # Create a prompt for the LLM
        prompt = f"""
{conversation}

You are a helpful assistant providing technology news up to September 2021.

Use the following articles to answer the user's question:

{context}

Question: {question}

Instructions:
- Summarize the most relevant information from the articles that answers the question.
- Only include information up to your knowledge cutoff in September 2021.
- Do not mention future dates or events beyond 2021.
- Present the information in a clear and concise manner.
- If multiple points are relevant, list them numerically.
- At the end of each point, invite the user to read more by providing the source URL.
- Ensure all information is accurate and verified.

Answer:
"""
        response = self.llm.invoke(prompt).content.strip()
        return response

    def handle_no_relevant_info(self, question: str) -> str:
        """
        Handles cases where no relevant information is found.

        Parameters:
            question (str): The user's question.

        Returns:
            str: The chatbot's response.
        """
        # Prepare conversation context
        conversation = self.format_chat_history()

        # Provide a general answer or inform the user
        prompt = f"""
{conversation}

You are a knowledgeable assistant.

The user asked: "{question}"

Unfortunately, no relevant information was found in the latest articles.

Instructions:
- Provide a helpful answer based on your general knowledge up to September 2021.
- Avoid mentioning any information beyond your knowledge cutoff.
- If the question is about recent events, politely inform the user that you don't have updated information.
- Offer assistance with other topics if appropriate.

Answer:
"""
        response = self.llm.invoke(prompt).content.strip()
        return response

    def handle_general_question(self, question: str) -> str:
        """
        Handles general questions that do not require IR.

        Parameters:
            question (str): The user's question.

        Returns:
            str: The chatbot's response.
        """
        # Prepare conversation context
        conversation = self.format_chat_history()

        # Continue the conversation using general knowledge
        prompt = f"""
{conversation}

You are a helpful assistant.

Instructions:
- Provide a clear and concise answer based on verified information up to your knowledge cutoff in September 2021.
- Avoid including any information that you're not sure about.
- Do not mention future events or speculate about the future.
- Be informative and helpful.
- Maintain a friendly and professional tone.

User: {question}
Assistant:
"""
        response = self.llm.invoke(prompt).content.strip()
        return response

    def format_chat_history(self) -> str:
        """
        Formats the chat history into a conversation string.

        Returns:
            str: Formatted conversation history.
        """
        conversation = ""
        for message in self.chat_history:
            role = "User" if message["role"] == "user" else "Assistant"
            content = message["content"]
            conversation += f"{role}: {content}\n"
        return conversation.strip()
