import time
import os
import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)

from core_logic.twitter_monitor import update_tweet_history, get_tweet_count, add_token_to_watchlist
from core_logic.gas_monitor import get_current_gas_price
from core_logic.executor import execute_trade
from core_logic.reddit_monitor import update_post_history, get_post_count
import json

# Simulated parsed GPT result
"""user_command = {
    "action": "buy",
    "token": "PEPE",
    "conditions": {
        "twitter_trending": True,
        "gas_price_threshold": 30
    }
}"""

#user_command = None
def load_latest_command():
    try:
        with open("parsed_command.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None

# Convert token to watchable format
#watch_token = f"${user_command['token'].upper()}"
#add_token_to_watchlist(watch_token)

#watch_token = None

def check_conditions(user_command):
    # Update recent tweet history (polls Twitter)

    #update_tweet_history()
    token = user_command['token']
    #amount = user_command['amount']
    update_post_history(token)

    #tweet_count = get_tweet_count(watch_token)
    post_count = get_post_count(token)
    gas_price = get_current_gas_price()

    #print(f"📈 Tweet count for {watch_token}: {tweet_count}")
    print(f"📈 Reddit post count for {token}: {post_count}")
    print(f"⛽ Current gas: {gas_price} gwei")

    #trending_ok = tweet_count > 10 if user_command["conditions"].get("twitter_trending") else True
    trending_ok = post_count >= 1 if user_command["conditions"].get("twitter_trending") else True
    #print("ACTUAL:", gas_price)
    #print("THRESHOLD:", user_command["conditions"].get("gas_price_threshold", 1000))


    gas_ok = gas_price < user_command["conditions"].get("gas_price_threshold", 1000)

    return trending_ok and gas_ok
    #return gas_ok

def main_loop():
    print("🌀 Scheduler started...")
    os.remove("parsed_command.json")

    while True:
        user_command = load_latest_command()
        if user_command:
            watch_token = f"${user_command['token'].upper()}"
            add_token_to_watchlist(watch_token)
            if check_conditions(user_command): # check_conditions() is true
                print(f"🎯 Conditions met! Would execute '{user_command['action']}' on {user_command['token']} now.")
                execute_trade(token_symbol=user_command['token'], amount=user_command['amount'])
                

            else:
                print("⏳ Conditions not met yet.")
            time.sleep(10)  # Run every minute
        else:
            print("⏳ Waiting for user command...")

        time.sleep(10)

        

if __name__ == "__main__":
    main_loop()
