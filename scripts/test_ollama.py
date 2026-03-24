import math
from datetime import datetime

from src.db.chunck_repo import ChunkRepository
from src.db.database import get_session
from src.embeddings.embedding import OllamaEmbedder
from utils.logger import setup_logger

log = setup_logger(__name__)


def main():

    session = get_session()
    chunk_repo = ChunkRepository(session=session)

    chunks = chunk_repo.get_all()

    texts = [chunk.content for chunk in chunks]
    log.info("All chunks %s", len(texts))

    bt = datetime.now()

    embedder = OllamaEmbedder()
    embeddings = embedder(texts)

    at = datetime.now() - bt

    log.info(
        "Embeddings completed successfully for %s input texts. and has the dimension %s, in %s seconds",
        len(embeddings),
        len(embeddings[0]),
        at,
    )

    # scores =[]

    # for embedding in embeddings:
    #     scores.append(cosine_similarity(embedding, embeddings[0]))
    #     scores.append(cosine_similarity(embedding, embeddings[1]))
    #     scores.append(cosine_similarity(embedding, embeddings[2]))
    #     scores.append(cosine_similarity(embedding, embeddings[3]))

    # return(scores)


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    return dot / (norm_a * norm_b)


if __name__ == "__main__":
    scores = main()
    # log.info("Scores are as follows %s", scores)
