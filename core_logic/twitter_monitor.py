import os
import time
import requests
from collections import defaultdict, deque
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
SEARCH_URL = "https://api.twitter.com/2/tweets/search/recent"

HEADERS = {
    "Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"
}

# Store timestamps of matching tweets per token
tweet_buffers = defaultdict(lambda: deque())

# List of tokens to monitor (can update dynamically later)
watchlist = []


def update_tweet_history():
    for token in watchlist:
        params = {
            "query": token.replace("$", ""), # Remove $ before querying
            "max_results": 10,  # limit to stay within free tier
        }

        response = requests.get(SEARCH_URL, headers=HEADERS, params=params)

        if response.status_code == 200:
            data = response.json()
            now = time.time()

            for tweet in data.get("data", []):
                tweet_buffers[token].append(now)
                print(f"Tweet for {token}: {tweet['text'][:50]}...")
        else:
            print(f"Error fetching tweets for {token}: {response.status_code}")

def get_tweet_count(token: str, window_sec: int = 600) -> int:
    now = time.time()
    buffer = tweet_buffers[token]
    while buffer and now - buffer[0] > window_sec:
        buffer.popleft()
    return len(buffer)

def add_token_to_watchlist(token: str):
    if token not in watchlist:
        watchlist.append(token)