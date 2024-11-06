from langchain_openai import ChatOpenAI
from app.chatbot.prompt_manager import PromptManager


class TechNewsChatbot:
    def __init__(self, api_key: str, retriever=None, persona="technical"):
        """
        Initializes the Tech News chatbot with a persona and a single OpenAI instance.

        Parameters:
            api_key (str): The API key for OpenAI.
            retriever: The information retriever instance (optional).
            persona (str): The user persona, either "technical" or "non-technical".
        """
        self.llm = ChatOpenAI(api_key=api_key, model_name="gpt-4o-mini", temperature=0.2)
        self.retriever = retriever
        self.chat_history = []
        self.persona_manager = PromptManager(persona)

        self.initial_instruction = (
            "You are a technical assistant focused on technology, programming, "
            "and tech industry trends. Keep responses within these topics and avoid unrelated discussions."
        )

    def ask_question(self, question: str) -> str:
        """
        Processes the user's question by first checking if it requires IR, and then generating the response.

        Parameters:
            question (str): The user's question.

        Returns:
            str: The chatbot's response.
        """
        ir_needed = self.check_ir_needed(question)
        print("IR needed:", ir_needed)

        if ir_needed and self.retriever is not None:
            response = self.handle_ir_question(question)
        else:
            response = self.handle_general_question(question)

        # Update chat history with labeled conversation
        self.chat_history.append({"role": "user", "content": question})
        self.chat_history.append({"role": "assistant", "content": response})

        return response

    def check_ir_needed(self, question: str) -> bool:
        """
        Uses a dedicated prompt to determine if the question requires information retrieval.

        Parameters:
            question (str): The user's question.

        Returns:
            bool: True if IR is needed, False otherwise.
        """
        ir_check_template = self.persona_manager.get_ir_check_template()
        ir_prompt = ir_check_template.format(question=f"Does this question require recent information: {question}")
        ir_response = self.llm.invoke(ir_prompt).content.strip()

        return "IR: yes" in ir_response

    def handle_ir_question(self, question: str) -> str:
        """
        Handles questions that require information retrieval, using recent tech news.

        Parameters:
            question (str): The user's question.

        Returns:
            str: The chatbot's response.
        """
        conversation = self.format_chat_history(window_size=3)
        contextualized_query = f"{conversation}\nUser: {question}"

        retrieved_docs = self.retriever.get_relevant_documents(contextualized_query)

        context = "\n\n".join(
            f"{idx + 1}. {doc.page_content}\nSource: {doc.metadata.get('source_name', 'Unknown')} | "
            f"Published: {doc.metadata.get('publishedAt', 'Unknown')}\nURL: {
                doc.metadata.get('url', 'URL not available')}"
            for idx, doc in enumerate(retrieved_docs)
        )

        ir_prompt_template = self.persona_manager.get_ir_prompt_template()
        prompt = ir_prompt_template.format(conversation=conversation, context=context, question=question)

        response = self.llm.invoke(prompt).content.strip()
        return response

    def handle_general_question(self, question: str) -> str:
        """
        Handles general questions that do not require recent updates.

        Parameters:
            question (str): The user's question.

        Returns:
            str: The chatbot's response.
        """
        general_prompt_template = self.persona_manager.get_general_prompt_template()
        conversation = self.format_chat_history(window_size=3)
        prompt = general_prompt_template.format(conversation=conversation, question=question)
        response = self.llm.invoke(prompt).content.strip()
        return response

    def format_chat_history(self, window_size: int = 3) -> str:
        """
        Formats the chat history into a conversation string, using a sliding window to include
        only the last `window_size` interactions for context. Labels each part clearly.

        Parameters:
            window_size (int): The number of previous interactions to include for context.

        Returns:
            str: Formatted conversation history.
        """
        num_messages = min(window_size * 2, len(self.chat_history))
        relevant_history = self.chat_history[-num_messages:]

        history_text = "\n".join(
            f"{'User' if msg['role'] == 'user' else 'Assistant'}: {msg['content']}"
            for msg in relevant_history
        )

        return f"{self.initial_instruction}\n\nPrevious conversation:\n{history_text}"
