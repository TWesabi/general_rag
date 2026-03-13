from src.chunking.fixed_size_chunker import FixedSizeChunker
from src.chunking.recursive_chunker import RecursiveChunker
from src.parsers.basic_cleaning import BasicTextCleaner
from src.utils.logger import setup_logger

log = setup_logger(__name__)


def main():

    text = """
    Retrieval-Augmented Generation: From Simple to Advanced Systems

Introduction to RAG

Retrieval-Augmented Generation, commonly known as RAG, represents one of the most significant advancements in the field of natural language processing and large language models. At its core, RAG is a framework that enhances the capabilities of generative models by incorporating external knowledge retrieval mechanisms. This approach addresses one of the fundamental limitations of traditional language models: their reliance on static training data and the subsequent inability to access or incorporate information beyond their training cutoff.

The basic premise of RAG is elegantly simple yet profoundly powerful. Instead of relying solely on the parametric knowledge stored within a model's weights, RAG systems first retrieve relevant information from an external knowledge source and then use this retrieved information to augment the generation process. This combination of retrieval and generation allows for more accurate, up-to-date, and contextually relevant responses.

Chapter 1: The Foundations of RAG

The Problem with Traditional Language Models

Traditional language models, including early transformer-based architectures, operate purely on the knowledge they acquired during training. Once trained, these models have no mechanism to access new information or verify facts against external sources. This creates several significant limitations:

First, the knowledge becomes stale over time. A model trained in 2021 has no awareness of events, discoveries, or developments that occurred after its training cutoff. Second, these models have no inherent mechanism for fact verification-they generate responses based on statistical patterns in their training data, which can lead to confident but incorrect statements, a phenomenon often called "hallucination." Third, the knowledge is implicit and distributed across billions of parameters, making it difficult to trace the source of information or update specific facts without retraining the entire model.

The Retrieval-Augmented Solution

RAG addresses these limitations by decoupling knowledge storage from generation capabilities. The generative model no longer needs to memorize all possible information; instead, it can focus on its core competency of understanding context and generating coherent text. The knowledge is stored externally in a retrievable format, typically a vector database or search index, which can be updated independently of the generative model.

This architectural separation offers several advantages. Knowledge can be updated simply by modifying the external database, without any retraining of the generative model. The retrieval step provides provenance-the system can cite sources and allow users to verify information. Additionally, the retrieval mechanism can be designed to access domain-specific knowledge bases, enabling the same generative model to serve specialized applications in medicine, law, or other fields.

Chapter 2: Simple RAG Systems

The Basic Architecture

A simple RAG system consists of three primary components: a retrieval mechanism, a knowledge base, and a generative model. The retrieval mechanism converts queries into a format suitable for searching the knowledge base. The knowledge base contains documents or passages that have been pre-processed and indexed. The generative model takes the original query along with the retrieved documents and produces a final response.

The retrieval process typically begins with embedding both the query and the documents in the knowledge base into a shared vector space. When a user submits a query, it is converted into an embedding vector, and the system searches for documents whose embeddings are closest to this query embedding. This similarity search returns the most relevant documents, which are then passed to the generative model along with the original query.

Implementation Considerations

In simple RAG implementations, several design choices significantly impact performance. The choice of embedding model determines how effectively semantic relationships are captured. Early systems often used pre-trained models like

Sentence-BERT or Instructor embeddings. The chunking strategy-how documents are divided into retrievable units-affects both retrieval accuracy and the amount of context provided to the generator. Common approaches include fixed-size chunks with overlap, sentence-level chunks, or paragraph-level chunks.

The generative model in simple RAG systems is typically a large language model that has been fine-tuned to effectively utilize retrieved context. The prompt template must instruct the model to base its response primarily on the provided context while acknowledging when the context lacks sufficient information to answer the query.
    """

    cleaner = BasicTextCleaner()
    clean_text = cleaner(text)
    chunk_size = 500
    overlap_size = 100

    chunker = FixedSizeChunker(chunk_size=chunk_size, chunk_overlap=overlap_size)
    chunks = chunker(clean_text)

    total = 0
    for chunk in chunks:
        total = total + len(chunk)
    average = total / len(chunks)
    log.info("Average chunk size is %s", average)
    log.info(
        "First 200 chars of first chunk is %s, its total length is %s",
        chunks[0][:200],
        len(chunks[0]),
    )
    log.info(
        "First 200 chars of last chunk is %s, its total length is %s",
        chunks[-1][:200],
        len(chunks[-1]),
    )
    log.info(
        "Fifth chunk is %s, its total length is %s",
        chunks[4],
        len(chunks[4]),
    )

    lengths = sorted([len(chunk) for chunk in chunks])

    log.info("shortest recursive chunks has a total length of %s", lengths[0])

    print(
        "\n ################################ Here starts the recursive results#####################################################\n "
    )
    print(
        "\n#######################################################################################################################\n"
    )

    recursive_chunker = RecursiveChunker(chunk_size=chunk_size, chunk_overlap=overlap_size)
    r_chunks = recursive_chunker(clean_text)

    r_total = 0
    for chunk in r_chunks:
        r_total = r_total + len(chunk)
    average = r_total / len(r_chunks)
    log.info("Average chunk size is %s", average)
    log.info(
        "First 200 chars of first recursive chunk is %s, its total length is %s",
        r_chunks[0][:200],
        len(r_chunks[0]),
    )
    log.info(
        "First 200 chars of last recursive chunk is %s, its total length is %s",
        r_chunks[-1][:200],
        len(r_chunks[-1]),
    )

    log.info(
        "Fifth recursive chunk is %s, its total length is %s",
        r_chunks[4],
        len(r_chunks[4]),
    )

    r_lengths = sorted([len(chunk) for chunk in r_chunks])

    log.info("shortest recursive chunks has a total length of %s", r_lengths[0])


if __name__ == "__main__":
    main()
