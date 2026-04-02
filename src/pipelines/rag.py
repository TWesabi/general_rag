from src.config import settings
from src.generation.generator import BaseGenerator
from src.retrieval.retriever import BaseRetriever


class RAGPipeline:
    def __init__(self, retriever: BaseRetriever, generator: BaseGenerator):
        self.retriever = retriever
        self.generator = generator

    def __call__(self, user_query: str) -> str:
        result = self.retriever(user_query=user_query, top_k=settings.TOP_K)
        answer = self.generator(user_query=user_query, context=result)
        return answer
