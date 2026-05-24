import os
import sys

import chromadb
from dotenv import load_dotenv
from google import genai
from google.genai import types


EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-2")
COLLECTION_NAME = "pokemon_market_reddit_gemini"


load_dotenv()


def embed_query(gemini_client, query):
    response = gemini_client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=query,
        config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
    )
    return response.embeddings[0].values


def retrieve(query, n_results=5):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set in .env")

    gemini_client = genai.Client(api_key=api_key)
    chroma_client = chromadb.PersistentClient(path="chroma_db")
    collection = chroma_client.get_collection(name=COLLECTION_NAME)

    query_embedding = embed_query(gemini_client, query)

    return collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )


def print_results(results):
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    for rank, (document, metadata, distance) in enumerate(
        zip(documents, metadatas, distances), start=1
    ):
        print("=" * 80)
        print("Rank:", rank)
        print("Cosine distance:", round(distance, 4))
        print("Title:", metadata["title"])
        print("Source:", metadata["permalink"])
        print()
        print(document[:700])


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit('Usage: python query_retrieval.py "your question here"')

    query_text = " ".join(sys.argv[1:])
    print_results(retrieve(query_text))
