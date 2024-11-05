from typing import Dict
from langchain_openai import ChatOpenAI
from app.chatbot.intent_classifier import RunInformationRetrievalClassifier
from app.chatbot.prompt_manager import PromptManager


class TechNewsChatbot:
    def __init__(self, api_key: str, retriever=None, persona="technical"):
        """
        Initializes the Tech News chatbot with a persona and uses OpenAI GPT for content filtering and response logic.

        Parameters:
            api_key (str): The API key for OpenAI.
            retriever: The information retriever instance (optional).
            persona (str): The user persona, either "technical" or "non-technical".
        """
        self.llm = ChatOpenAI(api_key=api_key, model_name="gpt-4o-mini", temperature=0.2)
        self.retriever = retriever
        self.chat_history = []
        self.ir_classifier = RunInformationRetrievalClassifier()
        self.persona_manager = PromptManager(persona)

    def ask_question(self, question: str) -> str:
        """
        Processes the user's question and generates an appropriate response using prompt engineering.

        Parameters:
            question (str): The user's question.

        Returns:
            str: The chatbot's response.
        """
        use_ir = self.ir_classifier.classify(question)
        print(f"IR Classifier returned: {use_ir}")

        if use_ir == "yes" and self.retriever is not None:
            response = self.handle_ir_question(question)
        else:
            response = self.handle_general_question(question)

        self.chat_history.append({"role": "user", "content": question})
        self.chat_history.append({"role": "assistant", "content": response})

        return response

    def handle_ir_question(self, question: str) -> str:
        """
        Handles questions that require information retrieval, using GPT-4 to decide if retrieved content is relevant.

        Parameters:
            question (str): The user's question.

        Returns:
            str: The chatbot's response.
        """
        retrieved_docs = self.retriever.get_relevant_documents(question)

        context = "\n\n".join(
            f"{idx + 1}. {doc.page_content}\nSource URL: {doc.metadata.get('url', 'URL not available')}"
            for idx, doc in enumerate(retrieved_docs)
        )
        prompt_template = self.persona_manager.get_ir_prompt_template()
        conversation = self.format_chat_history()
        prompt = prompt_template.format(conversation=conversation, context=context, question=question)

        response = self.llm.invoke(prompt).content.strip()
        return response

    def handle_general_question(self, question: str) -> str:
        """
        Handles general questions, filtering out non-tech-related questions and responding appropriately.

        Parameters:
            question (str): The user's question.

        Returns:
            str: The chatbot's response.
        """
        prompt_template = self.persona_manager.get_general_prompt_template()
        conversation = self.format_chat_history()
        prompt = prompt_template.format(conversation=conversation, question=question)
        print(prompt)
        response = self.llm.invoke(prompt).content.strip()
        return response

    def format_chat_history(self) -> str:
        """
        Formats the chat history into a conversation string, excluding behavior instructions.

        Returns:
            str: Formatted conversation history.
        """
        return "\n".join(
            f"{'User' if msg['role'] == 'user' else 'Assistant'}: {msg['content']}"
            for msg in self.chat_history
        )
