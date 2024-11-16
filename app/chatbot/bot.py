from langchain_openai import ChatOpenAI
from app.chatbot.prompt_manager import PromptManager


class TechNewsChatbot:
    def __init__(self, api_key: str, retriever=None, persona="technical"):
        """
        Initializes the Tech News chatbot with a persona and a OpenAI LLM instance.

        Parameters:
            api_key (str): The API key for OpenAI.
            retriever: The information retriever instance (optional).
            persona (str): The user persona, either "technical" or "non-technical".
        """
        self.llm = ChatOpenAI(api_key=api_key, model_name="gpt-4o-mini", temperature=0.2)
        self.retriever = retriever
        self.chat_history = []
        self.persona_manager = PromptManager(persona)

        self.initial_instruction = self.persona_manager.get_instructions()

    def ask_question(self, question: str) -> str:
        """
        Processes the user's question, decides if IR is needed, and generates the response.

        Parameters:
            question (str): The user's question.

        Returns:
            str: The chatbot's response.
        """
        self.current_question = question

        self.chat_history.append({"role": "user", "content": question})

        print("\n=== Chat History ===")
        for msg in self.chat_history:
            role = 'User' if msg['role'] == 'user' else 'Assistant'
            print(f"{role}: {msg['content']}")
        print("====================\n")

        if self.is_short_or_unclear(question):
            response = self.handle_short_input(question)
        else:
            ir_needed = self.check_ir_needed(question)
            print("IR needed:", ir_needed)

            if ir_needed and self.retriever is not None:
                response = self.handle_ir_question(question)
            else:
                response = self.handle_general_question(question)
        self.chat_history.append({"role": "assistant", "content": response})

        return response

    def is_short_or_unclear(self, text):
        """
        Determines if the user's input is short or unclear.

        Parameters:
            text (str): The user's input.

        Returns:
            bool: True if the input is short or potentially unclear.
        """
        return len(text.strip().split()) <= 2

    def handle_short_input(self, question: str) -> str:
        """
        Handles short or unclear user inputs.

        Parameters:
            question (str): The user's question.

        Returns:
            str: The chatbot's response.
        """
        short_input_template = self.persona_manager.get_short_input_template()
        conversation = self.format_chat_history(max_turns=2)
        prompt = short_input_template.format(conversation=conversation, question=question)

        print("\n=== Prompt for Short Input ===")
        print(prompt)
        print("================================\n")

        response = self.llm.invoke(prompt).content.strip()
        return response

    def check_ir_needed(self, question: str) -> bool:
        """
        Determines if the question requires information retrieval.

        Parameters:
            question (str): The user's question.

        Returns:
            bool: True if IR is needed, False otherwise.
        """
        ir_check_template = self.persona_manager.get_ir_check_template()
        ir_prompt = ir_check_template.format(question=question)

        print("\n=== IR Classifier Prompt ===")
        print(ir_prompt)
        print("============================\n")

        ir_response = self.llm.invoke(ir_prompt).content.strip()
        print("\n=== IR Classifier Response ===")
        print(f"'{ir_response}'")
        print("===============================\n")

        ir_decision = ir_response.strip().lower()
        ir_needed = ir_decision == "ir: yes"
        return ir_needed

    def handle_ir_question(self, question: str) -> str:
        """
        Handles questions that require information retrieval.

        Parameters:
            question (str): The user's question.

        Returns:
            str: The chatbot's response.
        """
        ir_query = self.generate_ir_query(question)

        print("\n=== Generated IR Query ===")
        print(ir_query)
        print("==========================\n")

        retrieved_docs = self.retriever.get_relevant_documents(ir_query)

        if retrieved_docs:
            context = "\n\n".join(
                f"{idx + 1}. {doc.page_content}\nSource: {doc.metadata.get('source_name', 'Unknown')} | "
                f"Published: {doc.metadata.get('publishedAt', 'Unknown')}\nURL: {
                    doc.metadata.get('url', 'URL not available')}"
                for idx, doc in enumerate(retrieved_docs)
            )

            ir_prompt_template = self.persona_manager.get_ir_prompt_template()
            conversation = self.format_chat_history(max_turns=3)
            prompt = ir_prompt_template.format(conversation=conversation, context=context, question=question)

            print("\n=== Final Prompt for IR Response ===")
            print(prompt)
            print("====================================\n")

            response = self.llm.invoke(prompt).content.strip()
        else:
            no_info_template = self.persona_manager.get_no_relevant_info_template()
            conversation = self.format_chat_history(max_turns=3)
            prompt = no_info_template.format(conversation=conversation, question=question)

            print("\n=== Final Prompt for No Info Response ===")
            print(prompt)
            print("=========================================\n")

            response = self.llm.invoke(prompt).content.strip()

        return response

    def generate_ir_query(self, question: str) -> str:
        """
        Generates an IR query based on the chat history and current question.

        Parameters:
            question (str): The user's question.

        Returns:
            str: The IR query.
        """
        ir_query_template = self.persona_manager.get_ir_query_template()
        conversation = self.format_chat_history_for_ir(max_turns=2)
        prompt = ir_query_template.format(conversation=conversation, question=question)

        print("\n=== IR Query Generation Prompt ===")
        print(prompt)
        print("==================================\n")

        ir_query_response = self.llm.invoke(prompt).content.strip()

        print("\n=== IR Query Generation Response ===")
        print(ir_query_response)
        print("====================================\n")

        return ir_query_response

    def handle_general_question(self, question: str) -> str:
        """
        Handles general questions that do not require recent information.

        Parameters:
            question (str): The user's question.

        Returns:
            str: The chatbot's response.
        """
        general_prompt_template = self.persona_manager.get_general_prompt_template()
        conversation = self.format_chat_history(max_turns=3)
        prompt = general_prompt_template.format(conversation=conversation, question=question)

        print("\n=== Final Prompt for General Response ===")
        print(prompt)
        print("==========================================\n")

        response = self.llm.invoke(prompt).content.strip()
        return response

    def format_chat_history(self, max_turns=3) -> str:
        """
        Formats the chat history for inclusion in prompts.

        Parameters:
            max_turns (int): The number of recent turns to include.

        Returns:
            str: The formatted chat history.
        """
        relevant_history = self.chat_history[-(max_turns * 2):]
        history_text = f"{self.initial_instruction}\n\nPrevious conversation:\n"

        for msg in relevant_history:
            role = 'User' if msg['role'] == 'user' else 'Assistant'
            history_text += f"{role}: {msg['content']}\n"

        print("\n=== Formatted Chat History ===")
        print(history_text)
        print("================================\n")

        return history_text

    def format_chat_history_for_ir(self, max_turns=2) -> str:
        """
        Formats the chat history specifically for IR query generation.

        Parameters:
            max_turns (int): The number of recent turns to include.

        Returns:
            str: The formatted chat history for IR.
        """
        recent_messages = self.chat_history[-(max_turns * 2):]
        history_text = ""

        for msg in recent_messages:
            role = 'User' if msg['role'] == 'user' else 'Assistant'
            history_text += f"{role}: {msg['content']}\n"

        print("\n=== Formatted Chat History for IR ===")
        print(history_text)
        print("=====================================\n")

        return history_text
