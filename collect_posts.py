import os
import praw
import json
from dotenv import load_dotenv

load_dotenv()


reddit = praw.Reddit(
    client_id = os.getenv("REDDIT_CLIENT_ID"),
    client_secret = os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent = "pkmntcg_rag_bot/0.1 by stene"
)

subreddit_name = "PokeInvesting"
subreddit = reddit.subreddit(subreddit_name)

submissions = []

for submission in subreddit.hot(limit=100):
    submissions.append({
        "id": submission.id,
        "subreddit": str(submission.subreddit),
        "title": submission.title,
        "body": submission.selftext,
        "score": submission.score,
        "num_comments": submission.num_comments,
        "created_utc": submission.created_utc,
        "url": submission.url,
        "permalink": "https://www.reddit.com" + submission.permalink
    })

with open("posts.json", "w", encoding="utf-8") as f:
    json.dump(submissions, f, indent=2)

print(f"Saved {len(submissions)} posts to posts.json")
