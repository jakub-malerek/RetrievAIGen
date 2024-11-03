import os
import datetime
from typing import List, Dict
from langchain.chat_models import ChatOpenAI
from langchain.schema import Document
from app.chatbot.intent_classifier import RunInformationRetrievalClassifier
from app.chatbot.personas import PersonaManager


class TechNewsChatbot:
    def __init__(self, api_key: str, retriever=None, persona="non-technical", debug=False):
        """
        Initializes the Tech News chatbot with a specified persona and debug mode.

        Parameters:
            api_key (str): The API key for OpenAI.
            retriever: The information retriever instance (optional).
            persona (str): The user persona, either "technical" or "non-technical".
            debug (bool): If True, writes IR system output to a file for debugging purposes.
        """
        self.llm = ChatOpenAI(api_key=api_key, model_name="gpt-4", temperature=0.2)
        self.retriever = retriever
        self.chat_history = []
        self.ir_classifier = RunInformationRetrievalClassifier()
        self.persona_manager = PersonaManager(persona)
        self.debug = debug
        self.debug_dir = "debug_logs"

        if self.debug:
            os.makedirs(self.debug_dir, exist_ok=True)

    def ask_question(self, question: str) -> str:
        """
        Processes the user's question and generates an appropriate response based on the persona.

        Parameters:
            question (str): The user's question.

        Returns:
            str: The chatbot's response.
        """
        self.chat_history.append({"role": "user", "content": question})

        use_ir = self.ir_classifier.classify(question)
        print(f"Classifier returned: {use_ir}")

        if use_ir == "yes" and self.retriever is not None:
            response = self.handle_ir_question(question)
        else:
            response = self.handle_general_question(question)

        self.chat_history.append({"role": "assistant", "content": response})

        return response

    def handle_ir_question(self, question: str) -> str:
        """
        Handles questions that require information retrieval and tailors the response based on the persona.

        Parameters:
            question (str): The user's question.

        Returns:
            str: The chatbot's response.
        """
        retrieved_docs = self.retriever.get_relevant_documents(question)

        if self.debug:
            self.write_ir_output_to_file(question, retrieved_docs)

        if not retrieved_docs:
            return self.handle_no_relevant_info(question)

        conversation = self.format_chat_history()

        formatted_docs = [
            f"{idx + 1}. {doc.page_content}\nSource URL: {doc.metadata.get('url', 'URL not available')}"
            for idx, doc in enumerate(retrieved_docs)
        ]
        context = "\n\n".join(formatted_docs)

        prompt_template = self.persona_manager.get_ir_prompt_template()
        prompt = prompt_template.format(conversation=conversation, context=context, question=question)

        response = self.llm.invoke(prompt).content.strip()
        return response

    def write_ir_output_to_file(self, question: str, documents: List[Document]):
        """
        Writes the IR system output to a file for debugging purposes.

        Parameters:
            question (str): The user's question.
            documents (List[Document]): The list of retrieved documents.
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.debug_dir, f"ir_output_{timestamp}.txt")

        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"Question: {question}\n\n")
            f.write("Retrieved Documents:\n\n")
            for idx, doc in enumerate(documents, start=1):
                url = doc.metadata.get('url', 'URL not available')
                f.write(f"Document {idx}:\n")
                f.write(f"Content:\n{doc.page_content}\n")
                f.write(f"Source URL: {url}\n")
                f.write("\n" + "-" * 80 + "\n\n")

        print(f"IR system output written to {filename}")

    def handle_general_question(self, question: str) -> str:
        """
        Handles general questions that do not require IR and tailors the response based on the persona.

        Parameters:
            question (str): The user's question.

        Returns:
            str: The chatbot's response.
        """
        conversation = self.format_chat_history()

        prompt_template = self.persona_manager.get_general_prompt_template()
        prompt = prompt_template.format(conversation=conversation, question=question)

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
        conversation = self.format_chat_history()

        prompt_template = self.persona_manager.get_no_relevant_info_template()
        prompt = prompt_template.format(conversation=conversation, question=question)

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
