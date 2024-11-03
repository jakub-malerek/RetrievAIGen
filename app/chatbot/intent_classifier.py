"""This module implements classifiers for different intents of user queries.
It is major component of Agentic Workflows, which is a conversational AI platform.
Based on the user query, the classifier determines whether the query requires external system to run"""

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer


class RunInformationRetrievalClassifier:
    def __init__(self, model_name="google/flan-t5-large"):
        """
        Initializes the classifier using instruction-tuned model like FLAN-T5 Large,
        with support for running on a CUDA-enabled GPU.

        Args:
            model_name (str): The name of the model to use.
        """
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self.model.to(self.device)

    def classify(self, user_input):
        """
        Classifies whether the user input requires information retrieval.

        Args:
            user_input (str): The user's input text.

        Returns:
            str: 'yes' if information retrieval is required, 'no' otherwise.
        """
        instruction = (
            "You are an AI assistant. Determine if the following user query requires retrieving "
            "the latest information, such as technology news, recent updates, or breaking news. "
            "Respond with 'yes' if the query asks for recent or time-sensitive information, "
            "otherwise respond with 'no'.\n\n"
            "Examples:\n"
            "1. User query: 'What are the latest updates in AI research?' -> yes\n"
            "2. User query: 'Explain how neural networks work.' -> no\n"
            "3. User query: 'What happened last week in cybersecurity?' -> yes\n"
            "4. User query: 'Define blockchain technology.' -> no\n"
            "5. User query: 'Any news on the latest iPhone release?' -> yes\n"
            "6. User query: 'How does a quantum computer work?' -> no\n"
            "7. User query: 'What’s trending in tech this month?' -> yes\n"
            "8. User query: 'Describe the process of software development.' -> no\n"
            "9. User query: 'Recent advancements in self-driving cars?' -> yes\n"
            "10. User query: 'What is the meaning of IoT?' -> no\n\n"
            f"User query: {user_input}"
        )

        inputs = self.tokenizer(instruction, return_tensors="pt").to(self.device)
        outputs = self.model.generate(**inputs, max_length=10, num_beams=5, early_stopping=True)

        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response.strip().lower()
