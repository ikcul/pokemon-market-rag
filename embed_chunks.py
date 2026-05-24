import json
import os

import chromadb
from dotenv import load_dotenv
from google import genai
from google.genai import types


EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-2")
COLLECTION_NAME = "pokemon_market_reddit_gemini"


load_dotenv()


def load_chunks(path="chunks.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def embed_document(gemini_client, text, title):
    response = gemini_client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_DOCUMENT",
            title=title,
        ),
    )
    return response.embeddings[0].values


def build_collection():
    chunks = load_chunks()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set in .env")

    gemini_client = genai.Client(api_key=api_key)
    chroma_client = chromadb.PersistentClient(path="chroma_db")

    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    for chunk in chunks:
        metadata = dict(chunk["metadata"])
        metadata["embedding_model"] = EMBEDDING_MODEL
        embedding = embed_document(
            gemini_client=gemini_client,
            text=chunk["text"],
            title=metadata["title"],
        )

        collection.upsert(
            ids=[chunk["chunk_id"]],
            documents=[chunk["text"]],
            metadatas=[metadata],
            embeddings=[embedding],
        )

        print(f"Upserted {chunk['chunk_id']}")

    print(f"Collection count: {collection.count()}")


if __name__ == "__main__":
    build_collection()
