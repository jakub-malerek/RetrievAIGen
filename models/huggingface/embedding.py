from typing import Union, List
import torch
from transformers import AutoModel, AutoTokenizer


class TextEmbedder:
    def __init__(self, model_name="avsolatorio/NoInstruct-small-Embedding-v0"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.model.eval()

    def get_embedding(self, text: Union[str, List[str]]):
        """
        Compute embeddings for a given text or list of texts.

        Parameters:
            text (Union[str, List[str]]): The input text or list of texts to embed.

        Returns:
            torch.Tensor: Embeddings for the input text(s).
        """
        if isinstance(text, str):
            text = [text]

        inp = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True)

        with torch.no_grad():
            output = self.model(**inp)

        embeddings = output.last_hidden_state.mean(dim=1)
        embeddings = embeddings.tolist()

        return embeddings
