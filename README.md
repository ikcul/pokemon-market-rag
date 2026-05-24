# Pokemon Market RAG

A native Python retrieval-augmented generation project for Pokemon TCG market discussion data.

The system collects Reddit posts from `r/PokeInvesting`, inspects whether the raw text is useful, fetches comments for thin-but-active posts, chunks the corpus, embeds the chunks with Gemini embeddings, and stores them in ChromaDB for semantic retrieval.

This project intentionally avoids LangChain and LlamaIndex so the mechanics are explicit and interview-defensible.

## Pipeline

```text
Reddit API
  -> posts.json
  -> inspection heuristics
  -> comments.json
  -> chunks.json
  -> Gemini embedding vectors
  -> ChromaDB cosine retrieval
```

## Setup

Create and activate a virtual environment, then install dependencies:

```bash
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Create a `.env` file:

```text
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
GEMINI_API_KEY=your_gemini_api_key
GEMINI_EMBEDDING_MODEL=gemini-embedding-2
```

Do not commit `.env`. It contains API secrets and is ignored by Git.

## Run The Pipeline

Collect Reddit posts:

```bash
.venv\Scripts\python.exe collect_posts.py
```

Inspect body quality:

```bash
.venv\Scripts\python.exe inspect_posts.py
```

Fetch comments for short, high-discussion posts:

```bash
.venv\Scripts\python.exe collect_comments.py
```

Build chunks:

```bash
.venv\Scripts\python.exe build_chunks.py
```

Embed chunks into ChromaDB:

```bash
.venv\Scripts\python.exe embed_chunks.py
```

Query retrieval:

```bash
.venv\Scripts\python.exe query_retrieval.py "What does the community think about Mega Greninja prices?"
```

## Embeddings

An embedding model converts text into a dense vector:

```text
"Should I hold sealed Pokemon 151?"
  -> [0.021, -0.884, 0.103, ...]
```

ChromaDB stores those vectors and retrieves chunks whose vectors are closest to the query vector. This project uses cosine distance, so lower distance means the query and chunk point in more similar semantic directions.

The configured embedding model is:

```text
gemini-embedding-2
```

All vectors in one Chroma collection must come from the same embedding model. If you change the embedding model, rebuild the Chroma collection by rerunning `embed_chunks.py`.

## Image-Heavy Reddit Posts

Image context cannot be solved by only changing the text embedding model.

The correct image-aware RAG pipeline is:

```text
Reddit image post
  -> use a multimodal Gemini model to describe/OCR the image
  -> save that image-derived text
  -> combine it with title/body/comments
  -> embed the combined text
```

For Pokemon market posts, the image-derived text should capture:

```text
card names
visible prices
graded card labels
sealed product names
store shelf prices
screenshotted market data
```

That text can then be embedded and retrieved like any other chunk.

## ChromaDB vs SQL

SQL databases are optimized for exact structured queries:

```sql
SELECT * FROM posts WHERE score > 100;
```

ChromaDB is optimized for semantic nearest-neighbor search:

```text
Given this query vector, return the stored vectors closest to it.
```

Chroma stores:

```text
id        -> stable chunk identifier
document  -> original chunk text
metadata  -> structured source fields
embedding -> dense float vector
```

SQL asks: which rows match this condition?

Chroma asks: which chunks are closest in meaning?

In a larger production system, SQL can be the source of truth and Chroma can be the semantic retrieval index.

## Files

```text
collect_posts.py        Pull Reddit submissions with PRAW
inspect_posts.py        Measure text quality before embedding
collect_comments.py     Fetch comments for posts that need discussion context
build_chunks.py         Convert posts/comments into retrieval chunks
embed_chunks.py         Embed chunks and upsert them into ChromaDB
query_retrieval.py      Embed a query and retrieve matching chunks
```

## Current Limitations

- The corpus currently covers Reddit data only.
- Image posts are not yet captioned or OCR'd.
- Price history and tournament results are not yet integrated.
- Generation is not wired yet; retrieval should be validated first.
