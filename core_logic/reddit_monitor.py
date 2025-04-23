import praw
import os
import time
from dotenv import load_dotenv
from collections import defaultdict, deque

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)

post_buffers = defaultdict(lambda: deque())

# These subreddits stay constant — you're just watching for different tokens
crypto_subreddits = [
    "CryptoCurrency",
    "CryptoMarkets",
    "CryptoMoonShots",
    "XRP"
]

seen_post_ids = set()

def update_post_history(token: str, window_sec: int = 1800):
    token = token.lower()
    now = time.time()

    for sub in crypto_subreddits:
        try:
            for post in reddit.subreddit(sub).new(limit=10):
                if post.id in seen_post_ids:
                    continue
                seen_post_ids.add(post.id)
                #print(post.title.lower())

                # Use the post's actual creation time
                created_at = post.created_utc

                if token in post.title.lower() and (now - created_at <= window_sec):
                    #post_buffers[token].append(now)
                    post_buffers[token].append(created_at)

                    print(f"📬 Reddit post in r/{sub}: {post.title[:80]}...")
        except Exception as e:
            print(f"❌ Error checking r/{sub}: {e}")

def get_post_count(token: str, window_sec: int = 1800):
    now = time.time()
    buffer = post_buffers[token.lower()]
    while buffer and now - buffer[0] > window_sec:
        buffer.popleft()
    return len(buffer)
