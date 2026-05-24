import json
import os
import sys

import praw
from dotenv import load_dotenv


load_dotenv()

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent="pkmntcg_rag_bot/0.1 by stene",
)


def load_posts(path="posts.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def post_needs_comments(post):
    body = post.get("body") or ""
    return len(body) < 100 and post.get("num_comments", 0) > 10


def fetch_top_level_comments(post_id, limit=10):
    submission = reddit.submission(id=post_id)
    submission.comments.replace_more(limit=0)

    comments = []
    for comment in submission.comments[:limit]:
        body = comment.body.strip()
        if body in {"[deleted]", "[removed]"}:
            continue

        comments.append(
            {
                "id": comment.id,
                "body": body,
                "score": comment.score,
                "created_utc": comment.created_utc,
                "permalink": "https://www.reddit.com" + comment.permalink,
            }
        )

    return comments


def collect_needed_comments(posts):
    records = []

    for post in posts:
        if not post_needs_comments(post):
            continue

        comments = fetch_top_level_comments(post["id"])
        records.append(
            {
                "post_id": post["id"],
                "post_title": post["title"],
                "post_permalink": post["permalink"],
                "comments": comments,
            }
        )

        print(f"Fetched {len(comments)} comments for: {post['title']}")

    return records


if __name__ == "__main__":
    posts = load_posts()
    comment_records = collect_needed_comments(posts)

    with open("comments.json", "w", encoding="utf-8") as f:
        json.dump(comment_records, f, indent=2)

    print(f"Saved comment records for {len(comment_records)} posts to comments.json")
