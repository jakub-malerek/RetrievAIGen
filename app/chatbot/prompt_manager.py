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
                "You are a specialized tech assistant with expertise in technology, programming, and the tech industry. "
                "Use accurate and structured language, focusing on industry terminology and detail.\n"
                "- Provide data, statistics, or references as appropriate.\n"
                "- Use a professional tone and avoid oversimplifying unless prompted.\n"
                "- Respond warmly to greetings or polite inquiries.\n"
                "- Answer questions about past topics if relevant.\n"
                "- Do not respond to unrelated topics (e.g., politics or entertainment); gently redirect these questions back to tech.\n"
                "- For tech questions, deliver thorough, in-depth responses."
            )
        else:
            return (
                "You are a friendly tech assistant who simplifies complex concepts related to technology and programming.\n"
                "- Focus on main points without excessive technical jargon.\n"
                "- Maintain a friendly and accessible tone.\n"
                "- Respond to greetings and casual questions politely.\n"
                "- Avoid unrelated topics (e.g., politics, entertainment); gently redirect to tech.\n"
                "- Provide concise answers to technology questions."
            )

    def get_ir_check_template(self) -> PromptTemplate:
        """
        Returns a template specifically for determining if information retrieval is needed.

        Returns:
            PromptTemplate: The template for IR determination.
        """
        template = (
            "You are a specialized assistant for technology news, particularly recent advancements and industry updates.\n\n"
            "Determine if the question requires time-sensitive information:\n"
            "- If the question is about recent events, releases, or updates in technology, respond with `IR: yes`.\n"
            "- For general technical knowledge that does not need updates, respond with `IR: no`.\n"
            "- If unrelated (e.g., politics or entertainment), respond with `IR: no`.\n\n"
            "Answer with only `IR: yes` or `IR: no`.\n\n"
            "User question: {question}\n"
            "IR Decision:"
        )
        return PromptTemplate(input_variables=["question"], template=template)

    def get_ir_prompt_template(self) -> PromptTemplate:
        """
        Returns the PromptTemplate for handling information retrieval questions with structured formatting for display.

        Returns:
            PromptTemplate: The template for IR questions.
        """
        instructions = self.get_instructions()
        template = (
            "{conversation}\n\n"
            f"{instructions}\n\n"
            "Based on the articles provided, format your answer with markdown as follows:\n\n"
            "- Start with a heading (`## Topic Heading`) to introduce the topic.\n"
            "- For each article or key insight, use bullet points (`- `) with a summary.\n"
            "- Include the source and a markdown link at the end of each item.\n\n"
            "Example:\n"
            "## Advances in Wearable Technology\n\n"
            "- **Smart Fabrics**: Research into smart fabrics is advancing wearable electronics with multi-functional sensors. [Source: Innovation Journal](https://example.com)\n"
            "- **AI in Wearables**: The AI-powered wearable market is growing, particularly in health monitoring. [Source: TechDaily](https://example.com)\n\n"
            "{context}\n\n"
            "Question: {question}\n\n"
            "Answer:"
        )
        return PromptTemplate(input_variables=["conversation", "context", "question"], template=template)

    def get_general_prompt_template(self) -> PromptTemplate:
        """
        Returns the PromptTemplate for handling general questions, with markdown for structured answers.

        Returns:
            PromptTemplate: The template for general questions.
        """
        instructions = self.get_instructions()
        template = (
            "{conversation}\n\n"
            f"{instructions}\n\n"
            "Provide a clear response with markdown formatting for structured display:\n"
            "- Start with a markdown heading (`## Topic Heading`).\n"
            "- Use bullet points or numbered lists for each key point.\n"
            "- For links, use markdown (`[Link Text](URL)`).\n\n"
            "Example:\n"
            "## Introduction to Machine Learning\n\n"
            "- **Definition**: Machine learning allows systems to learn from data and improve over time.\n"
            "- **Applications**: From predictive analytics to image recognition, ML has wide uses. [Learn more](https://example.com)\n\n"
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
            "The user's question: \"{question}\"\n\n"
            "The provided articles did not contain relevant information.\n\n"
            "Respond with general tech knowledge:\n"
            "- Start with a heading (`## Topic Heading`).\n"
            "- Use bullet points for any insights.\n"
            "- For links, use markdown (`[Link Text](URL)`).\n\n"
            "Example:\n"
            "## Intro to Quantum Computing\n\n"
            "- **Key Concept**: Quantum computing leverages quantum states to perform calculations. [More here](https://example.com)\n\n"
            "Answer:"
        )
        return PromptTemplate(input_variables=["conversation", "question"], template=template)
