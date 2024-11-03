"""This module implements personas for the chatbot.
Personas are used to simulate different types of users and adjust the chatbot's responses accordingly."""

from langchain.prompts import PromptTemplate


class PersonaManager:
    def __init__(self, persona: str):
        """
        Initializes the PersonaManager with the specified persona.

        Parameters:
            persona (str): The persona type, either "technical" or "non-technical".
        """
        self.persona = persona

    def get_instructions(self) -> str:
        """
        Returns the appropriate instructions based on the persona.

        Returns:
            str: Instructions for the language model.
        """
        if self.persona == "technical":
            return (
                "You are a technical assistant providing in-depth and detailed information. "
                "Use precise technical language and include specific details where possible."
                "\n- Present information in a clear and structured manner."
                "\n- Use industry-specific terminology appropriately."
                "\n- Include relevant data, statistics, or references when applicable."
            )
        else:
            return (
                "You are a non-technical assistant providing simplified and high-level overviews. "
                "Use simple language and avoid jargon, explaining concepts in an easy-to-understand way."
                "\n- Present information in a clear and concise manner."
                "\n- Use analogies or examples to help explain complex topics."
                "\n- Focus on the main points without excessive detail."
            )

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
            "Use the following articles to answer the user's question:\n\n"
            "{context}\n\n"
            "Question: {question}\n\n"
            "Instructions:\n"
            "- Summarize the most relevant information from the articles that answers the question.\n"
            "- Only include information up to your knowledge cutoff in September 2021.\n"
            "- Do not mention future dates or events beyond 2021.\n"
            "- If multiple points are relevant, list them numerically.\n"
            "- At the end of each point, invite the user to read more by providing the source URL.\n"
            "- Ensure all information is accurate and verified.\n\n"
            "Answer:"
        )
        return PromptTemplate(
            input_variables=["conversation", "context", "question"], template=template
        )

    def get_general_prompt_template(self) -> PromptTemplate:
        """
        Returns the PromptTemplate for handling general questions.

        Returns:
            PromptTemplate: The template for general questions.
        """
        instructions = self.get_instructions()
        template = (
            "{conversation}\n\n"
            f"{instructions}\n\n"
            "Instructions:\n"
            "- Provide a clear and concise answer based on verified information up to your knowledge cutoff in September 2021.\n"
            "- Avoid including any information that you're not sure about.\n"
            "- Do not mention future events or speculate about the future.\n"
            "- Be informative and helpful, maintaining a friendly and professional tone.\n\n"
            "User: {question}\n"
            "Assistant:"
        )
        return PromptTemplate(input_variables=["conversation", "question"], template=template)

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
            "Unfortunately, no relevant information was found in the latest articles.\n\n"
            "Instructions:\n"
            "- Provide a helpful answer based on your general knowledge up to September 2021.\n"
            "- Avoid mentioning any information beyond your knowledge cutoff.\n"
            "- If the question is not related to technology or programming, politely refuse to answer and remind the user of your focus area.\n"
            "- If the question is about recent events, inform the user that you don't have updated information.\n"
            "- Offer assistance with other tech-related topics if appropriate.\n\n"
            "Answer:"
        )
        return PromptTemplate(
            input_variables=["conversation", "question"], template=template
        )
