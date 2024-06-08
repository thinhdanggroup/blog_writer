from abc import ABC, abstractmethod
from langchain_community.embeddings import OllamaEmbeddings


class EmbeddingModel(ABC):
    
    @abstractmethod
    def embed_query(self, query: str) -> list:
        pass
    
class OllamaEmbedding(EmbeddingModel):
    def __init__(self, model: str = "llama2:7b"):
        self.model = OllamaEmbeddings(model=model)
        
    def embed_query(self, query: str) -> list:
        return self.model.embed_query(query)
    
    
if __name__ == "__main__":
    model = OllamaEmbedding(model="mxbai-embed-large")
    print(model.embed_query("Hello World"))