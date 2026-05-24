import json


def load_posts(path="posts.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def inspect_posts(posts):
    total = len(posts)
    if total == 0:
        print("No posts found.")
        return

    body_lengths = [len(post.get("body") or "") for post in posts]
    empty_bodies = sum(length == 0 for length in body_lengths)

    needs_comments = [
        post
        for post, body_length in zip(posts, body_lengths)
        if body_length < 100 and post.get("num_comments", 0) > 10
    ]

    print("Total posts:", total)
    print("Empty bodies:", empty_bodies)
    print("Percent empty:", round(empty_bodies / total, 3))
    print("Average body length:", round(sum(body_lengths) / total, 1))
    print("Max body length:", max(body_lengths))
    print("Posts likely needing comments:", len(needs_comments))

    print("\nExamples likely needing comments:")
    for post in needs_comments[:10]:
        print("-" * 80)
        print("Title:", post["title"])
        print("Body length:", len(post.get("body") or ""))
        print("Comments:", post["num_comments"])
        print("URL:", post.get("permalink") or post.get("url"))


if __name__ == "__main__":
    inspect_posts(load_posts())
