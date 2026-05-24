import json
import re


MAX_CHARS = 1200


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize_text(text):
    return re.sub(r"\s+", " ", text).strip()


def split_paragraphs(text):
    return [normalize_text(part) for part in re.split(r"\n\s*\n", text) if part.strip()]


def chunk_text(text, max_chars=MAX_CHARS):
    paragraphs = split_paragraphs(text)
    chunks = []
    current = ""

    for paragraph in paragraphs:
        if not current:
            current = paragraph
        elif len(current) + len(paragraph) + 2 <= max_chars:
            current = f"{current}\n\n{paragraph}"
        else:
            chunks.append(current)
            current = paragraph

    if current:
        chunks.append(current)

    return chunks


def comments_by_post_id(comment_records):
    return {record["post_id"]: record["comments"] for record in comment_records}


def build_post_document(post, comments):
    sections = [f"Title: {post['title']}"]

    body = normalize_text(post.get("body") or "")
    if body:
        sections.append(f"Post body: {body}")

    if comments:
        comment_lines = [
            f"- score {comment['score']}: {normalize_text(comment['body'])}"
            for comment in comments
        ]
        sections.append("Top comments:\n" + "\n".join(comment_lines))

    return "\n\n".join(sections)


def build_chunks(posts, comment_records):
    comment_lookup = comments_by_post_id(comment_records)
    chunks = []

    for post in posts:
        post_comments = comment_lookup.get(post["id"], [])
        document = build_post_document(post, post_comments)

        for index, text in enumerate(chunk_text(document)):
            chunks.append(
                {
                    "chunk_id": f"reddit_post:{post['id']}:{index}",
                    "text": text,
                    "metadata": {
                        "source_type": "reddit_post",
                        "post_id": post["id"],
                        "subreddit": post["subreddit"],
                        "title": post["title"],
                        "score": post["score"],
                        "num_comments": post["num_comments"],
                        "created_utc": post["created_utc"],
                        "permalink": post["permalink"],
                    },
                }
            )

    return chunks


if __name__ == "__main__":
    posts = load_json("posts.json")
    comment_records = load_json("comments.json")
    chunks = build_chunks(posts, comment_records)

    with open("chunks.json", "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2)

    print(f"Saved {len(chunks)} chunks to chunks.json")
