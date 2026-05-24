import json

def analyze_and_route_data(source_file="posts.json"):
    # analyzing how we decide to chunk the posts given our json file
    with open("submissions.json", "r", encoding="utf-8") as f:
        submissions = json.load(f)

    total = len(submissions)

    empty_bodies = 0
    body_lengths = []
    needs_comments = []

    for post in submissions:
        body = post.get("body", "") or ""
        body_length = len(body)

        body_lengths.append(body_length)

        if body_length == 0:
            empty_bodies += 1

        if body_length < 100 and post.get("num_comments", 0) > 10:
            needs_comments.append(post)

    print("Total posts:", total)
    print("Empty bodies:", empty_bodies)
    print("Percent empty:", empty_bodies / total)
    print("Average body length:", sum(body_lengths) / total)
    print("Max body length:", max(body_lengths))
    print("Posts likely needing comments:", len(needs_comments))

    print("\nExamples that likely need comments:")
    for post in needs_comments[:len(needs_comments)]:
        print("-" * 80)
        print("Title:", post["title"])
        print("Body length:", len(post.get("body", "") or ""))
        print("Comments:", post["num_comments"])
        print("URL:", post["permalink"])

def execute_standard_post_chunking(submissions):
    print("[STRATEGY SELECTED]: Standard Document Chunking")
    print("-> Reasoning: Most posts contain robust body text.")
    print("-> Action: Processing Title + Selftext directly into chunks.\n")

    chunks_to_embed = []
    for post in submissions:
        # Combine title and body to keep full context together
        combined_text = f"Title: {post['title']}\nContent: {post.get('body', '')}"

        # Placeholder: This is where your text splitter logic will live
        # e.g., chunks_to_embed.extend(text_splitter(combined_text))
        chunks_to_embed.append(
            {"text": combined_text, "source_id": post.get("permalink")}
        )

    print(f"Prepared {len(chunks_to_embed)} document chunks for embedding.")
    # save_chunks(chunks_to_embed)

def execute_comment_aware_chunking(submissions):
    print("[STRATEGY SELECTED]: Comment-Augmented Pipeline")
    print("-> Reasoning: High volume of title-only or media-only posts with rich discussions.")
    print("-> Action: HALT embedding. Run a secondary comment-fetching script first.")
    print("-> Next Strategy: Build a map where Chunks = Title + High-Score Comments.\n")

    # Instead of wasting money embedding empty bodies, you route to a script
    # that builds payloads like:
    # "Context: [Title] | Discussion Point: [Top Comment Text]"
    pass

def execute_image_aware_chunking(submissions):
    print("[STRATEGY SELECTED]: Image-Augmented Pipeline")
    print("-> Reasoning: Title and subtext in post serve a small portion of the engagement and most of the engagement lies in the image")
    print("-> ")
    for post in submissions:
        post_data = {
            "title": post.title,
            "body": post.selftext,
            "permalink": post.permalink,
            "is_media": False,
            "media_urls": []
        }
    
    # 1. Handle Single Image Posts (hosted directly on Reddit)
    if hasattr(post, "post_hint") and post.post_hint == "image":
        post_data["is_media"] = True
        post_data["media_urls"].append(post.url)
        
    # 2. Handle Reddit Gallery Posts (multiple images in one post)
    elif hasattr(post, "is_gallery") and post.is_gallery:
        post_data["is_media"] = True
        # Extract URLs from the gallery metadata dictionary
        for item in post.gallery_data.get("items", []):
            media_id = item.get("media_id")
            if media_id:
                # Reconstruct the direct image URL from the media ID
                ext = post.media_metadata[media_id].get("m", "image/png").split("/")[-1]
                img_url = f"https://i.redd.it/{media_id}.{ext}"
                post_data["media_urls"].append(img_url)

    submissions.append(post_data)

if __name__ == "__main__":
    # Run the router
    analyze_and_route_data("posts.json")