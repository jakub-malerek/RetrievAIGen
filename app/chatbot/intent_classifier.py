import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer


class RunInformationRetrievalClassifier:
    def __init__(self, model_name="google/flan-t5-large"):
        """
        Initializes the classifier using an instruction-tuned model like FLAN-T5 Large,
        with support for running on a CUDA-enabled GPU.

        Args:
            model_name (str): The name of the model to use.
        """
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self.model.to(self.device)

    def classify(self, user_input: str) -> str:
        """
        Classifies whether the user input requires information retrieval for tech-related content.

        Args:
            user_input (str): The user's input text.

        Returns:
            str: 'yes' if the query asks for tech-related, time-sensitive information requiring IR,
                 'no' otherwise.
        """
        instruction = (
            "You are an AI assistant. Determine if the following user query requires retrieving "
            "the latest information, such as technology news, recent updates, or breaking news, "
            "and ensure the query is related to technology, programming, or the tech industry. "
            "Respond with 'yes' if the query both asks for recent or time-sensitive tech-related information, "
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
            "10. User query: 'What is the meaning of IoT?' -> no\n"
            "11. User query: 'Can you give me the latest trends in renewable energy?' -> no\n"
            "12. User query: 'What’s new in the world of quantum computing?' -> yes\n"
            "13. User query: 'How do I bake a cake?' -> no\n"
            "14. User query: 'Any breaking news on cybersecurity threats?' -> yes\n"
            "15. User query: 'Tell me about the latest developments in AI ethics.' -> yes\n\n"
            f"User query: {user_input}"
        )

        inputs = self.tokenizer(instruction, return_tensors="pt").to(self.device)
        outputs = self.model.generate(**inputs, max_length=10, num_beams=5, early_stopping=True)
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        return response.strip().lower()
