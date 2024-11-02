"""This module implements the InformationRetrievalClassifier class for determining whether to perform information retrieval for LLM context.
    This is major component of Agentic AI's chatbot system."""

from transformers import pipeline


class InformationRetrievalClassifier:
    def __init__(self, model_name="facebook/bart-large-mnli", device=-1):
        """
        Initializes the zero-shot classification pipeline for determining whether to perform information retrieval.

        Args:
            model_name (str): The name of the pre-trained model to use.
            device (int, optional): Device to run the model on. -1 for CPU, >=0 for GPU device index.
        """
        self.classifier = pipeline("zero-shot-classification", model=model_name, device=device)

    def heuristic_requires_ir(self, user_input):
        """
        Applies heuristic rules to quickly determine if information retrieval is needed.

        Args:
            user_input (str): The user's input text.

        Returns:
            bool: True if heuristics suggest IR is required, False otherwise.
        """
        keywords = [
            "latest news", "recent updates", "new in tech", "technology news",
            "tech headlines", "AI advancements", "software releases", "tech events",
            "tech news", "technology updates", "recent tech developments",
            "what's new in", "news about", "updates on", "latest in", "breaking news"
        ]
        user_input_lower = user_input.lower()
        for keyword in keywords:
            if keyword in user_input_lower:
                return True
        return False

    def requires_information_retrieval(self, user_input):
        """
        Determines whether information retrieval is required for the user's input.

        Args:
            user_input (str): The user's input text.

        Returns:
            str: 'yes' if information retrieval is required, 'no' otherwise.
        """
        if self.heuristic_requires_ir(user_input):
            return "yes"
        else:
            candidate_labels = ["request for tech news", "casual conversation", "general question"]
            result = self.classifier(user_input, candidate_labels)
            top_label = result['labels'][0]
            if top_label == "request for tech news":
                return "yes"
            else:
                return "no"
