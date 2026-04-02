from src.factory import create_rag_pipeline
from src.schemas.query import RetrievalResult

if __name__ == "__main__":

    user_query = "What are the benefits of retrieval-augmented generation?"

    test_context = [
        RetrievalResult(
            content="Retrieval-Augmented Generation (RAG) reduces hallucinations by grounding LLM responses in factual, retrieved documents rather than relying solely on parametric memory.",
            score=0.92,
            document_id=1,
            position=0,
        ),
        RetrievalResult(
            content="RAG systems allow organizations to keep their knowledge base up to date without retraining the underlying language model, significantly lowering operational costs.",
            score=0.87,
            document_id=1,
            position=3,
        ),
        RetrievalResult(
            content="By citing source documents, RAG architectures improve transparency and allow users to verify the information provided, increasing trust in AI-generated answers.",
            score=0.81,
            document_id=2,
            position=1,
        ),
    ]

    pipeline = create_rag_pipeline()
    answer = pipeline("What is RAG?")
    print(answer)
