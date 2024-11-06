from langchain.prompts import PromptTemplate


class PromptManager:
    def __init__(self, persona: str):
        """
        Initializes the PromptManager with the specified persona.

        Parameters:
            persona (str): The persona type, either "technical" or "non-technical".
        """
        self.persona = persona

    def get_instructions(self) -> str:
        """
        Returns instructions based on the persona, including support for conversational interactions.

        Returns:
            str: Instructions for the language model.
        """
        if self.persona == "technical":
            return (
                "You are a technical assistant who provides in-depth, accurate, and detailed information "
                "related to technology, programming, and the tech industry. "
                "Use precise, structured language and appropriate technical terminology.\n"
                "- Include data, statistics, or references when necessary.\n"
                "- Maintain a professional tone and do not simplify complex topics unless asked to.\n"
                "- Respond warmly to general conversation prompts like greetings and polite inquiries.\n"
                "- Answer memory-based questions about past conversation context when possible.\n"
                "- Do not respond to topics unrelated to technology, such as politics, entertainment, or unrelated fields. "
                "Gently redirect these questions to tech-related topics if needed.\n"
                "- For technology-related questions, give detailed, technical answers."
            )
        else:
            return (
                "You are a non-technical assistant who provides clear, simplified overviews "
                "related to technology, programming, and the tech industry. "
                "Use straightforward language that is easy to understand.\n"
                "- Focus on the main points without excessive technical detail.\n"
                "- Maintain a friendly and informative tone.\n"
                "- Respond to general conversation prompts and memory-based queries (e.g., past questions) appropriately.\n"
                "- Avoid responding to topics unrelated to technology, like politics or entertainment, "
                "and gently redirect these questions to technology topics.\n"
                "- For technology-related questions, keep answers concise and accessible."
            )

    def get_ir_check_template(self) -> PromptTemplate:
        """
        Returns a template specifically for determining if information retrieval is needed.
        This template is focused solely on answering whether recent news or updates are required.

        Returns:
            PromptTemplate: The template for IR determination.
        """
        template = (
            "You are an advanced technology news assistant, specifically focused on technology-related questions. "
            "Your role is to decide if the user's question requires recent, time-sensitive information in the field of technology. "
            "This includes fields like artificial intelligence, cybersecurity, programming, gadgets, and other tech-related updates.\n\n"
            "The RAG system is designed to provide responses to recent developments by retrieving up-to-date, contextually relevant "
            "information from a technology-focused knowledge base, similar to how a human would search for tech news, read reports, or consult recent articles.\n\n"
            "Instructions:\n"
            "- If the user's question is about recent events, new releases, or updates in technology (e.g., 'What are the latest trends in AI?'), "
            "respond with `IR: yes` to indicate that information retrieval is necessary.\n"
            "- If the question can be answered based on general technical knowledge without needing recent updates (e.g., 'What is Python?'), "
            "respond with `IR: no` to indicate that information retrieval is not required.\n"
            "- If the question is unrelated to technology (e.g., about politics, entertainment, personal advice, or other non-tech topics), "
            "respond with `IR: no` as these topics are outside the assistant's scope.\n\n"
            "Important:\n"
            "Please focus only on determining whether recent technology news or updates are required and provide only `IR: yes` or `IR: no` "
            "as your response, without any additional commentary or explanation.\n\n"
            "User question: {question}\n"
            "IR Decision:"
        )

        return PromptTemplate(input_variables=["question"], template=template)

    def get_ir_prompt_template(self) -> PromptTemplate:
        """
        Returns the PromptTemplate for handling information retrieval questions.

        Returns:
            PromptTemplate: The template for IR questions.
        """
        instructions = self.get_instructions()
        template = (
            "{conversation}\n\n"
            f"{instructions}\n\n"
            "You have been provided with several articles to assist in answering the user's question. "
            "Summarize each relevant article briefly, presenting the summaries as a numbered list:\n"
            "- [1] Provide a brief explanation of the key points.\n"
            "- [2] Invite the user to read more, followed by the source URL.\n"
            "- Mention if some articles are loosely related or irrelevant.\n\n"
            "Guidelines:\n"
            "- Answer tech-related questions only.\n"
            "- If unrelated, gently redirect to tech topics.\n\n"
            "Articles:\n\n"
            "{context}\n\n"
            "Question: {question}\n\n"
            "Answer:"
        )
        return PromptTemplate(
            input_variables=["conversation", "context", "question"], template=template
        )

    def get_general_prompt_template(self) -> PromptTemplate:
        """
        Returns the PromptTemplate for handling general questions without IR determination,
        focusing solely on answering the user's question based on existing knowledge.

        Returns:
            PromptTemplate: The template for general questions.
        """
        instructions = self.get_instructions()
        template = (
            "{conversation}\n\n"
            f"{instructions}\n\n"
            "Answer the user's question clearly and accurately based on your knowledge of technology and programming.\n\n"
            "If the question is related to casual conversation (e.g., greetings, past questions, or suggestions), "
            "respond appropriately while maintaining your technology expertise.\n\n"
            "User: {question}\n"
            "Assistant:"
        )
        return PromptTemplate(
            input_variables=["conversation", "question"], template=template
        )

    def get_no_relevant_info_template(self) -> PromptTemplate:
        """
        Returns the PromptTemplate for handling cases where no relevant information is found.

        Returns:
            PromptTemplate: The template for no relevant info responses.
        """
        instructions = self.get_instructions()
        template = (
            "{conversation}\n\n"
            f"{instructions}\n\n"
            "The user asked: \"{question}\"\n\n"
            "The provided articles did not contain relevant information.\n\n"
            "Please offer a helpful response based on your general knowledge. "
            "If the question is unrelated to technology or programming, respond with: "
            "\"I'm sorry, but I specialize in technology and programming topics. "
            "Please ask something related to these areas.\"\n\n"
            "Answer:"
        )
        return PromptTemplate(
            input_variables=["conversation", "question"], template=template
        )
