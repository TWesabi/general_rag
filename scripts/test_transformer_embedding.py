import math

from src.embeddings.transformer_embedding import TransformerEmbedder
from utils.logger import setup_logger

log = setup_logger(__name__)


def main():

    embedder = TransformerEmbedder()
    # embedder = OllamaEmbedder()
    embeddings = embedder(["hello", "world"])

    scores = []

    for embedding in embeddings:
        scores.append(cosine_similarity(embedding, embeddings[0]))
        scores.append(cosine_similarity(embedding, embeddings[1]))

    return (scores, embeddings)


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    return dot / (norm_a * norm_b)


if __name__ == "__main__":
    scores, embeddings = main()
    log.info("Scores are as follows %s", scores)
    log.info("Embeddings shape %s", len(embeddings))
    log.info("Embeddings type %s", type(embeddings))
