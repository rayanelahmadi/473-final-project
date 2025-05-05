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
from bot.handlers import notify_user
import asyncio

def load_latest_command():
    try:
        with open("parsed_command.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def check_conditions(user_command):

    token = user_command['token']
    update_post_history(token)

    post_count = get_post_count(token)
    gas_price = get_current_gas_price()

    print(f"Reddit post count for {token}: {post_count}")
    print(f"Current gas: {gas_price} gwei")



    

    trending_ok = post_count >= 0 if user_command["conditions"].get("reddit_trending") else False

    gas_ok = gas_price < user_command["conditions"].get("gas_price_threshold", 1000)

    return [trending_ok, gas_ok]

def main_loop():
    print("Scheduler started...")
    try:
        os.remove("parsed_command.json")
    except FileNotFoundError:
        pass

    while True:
        user_command = load_latest_command()
        if user_command:
            watch_token = f"${user_command['token'].upper()}"
            add_token_to_watchlist(watch_token)
            if check_conditions(user_command)[1]: # If gas is low enough
                if check_conditions(user_command)[0]: # If 'trending' on Reddit is True
                    if user_command['action'] == 'buy':
                        print(f"Conditions met! Would execute '{user_command['action']}' on {user_command['token']} now.")
                        asyncio.run(notify_user(f"Conditions met! Would execute '{user_command['action']}' on {user_command['token']} now."))

                        execute_trade(token_symbol=user_command['token'], amount=user_command['amount'], buy=True)
                        break
                    else:
                        print("Reddit still trending.")

                else:
                    if user_command['action'] == 'sell':
                        print(f"Conditions met! Would execute '{user_command['action']}' on {user_command['token']} now.")
                        asyncio.run(notify_user(f"Conditions met! Would execute '{user_command['action']}' on {user_command['token']} now."))

                        execute_trade(token_symbol=user_command['token'], amount=user_command['amount'], buy=False)
                        break
                    else:
                        print("Reddit trending condition not met yet.")

            else:
                print("Gas conditions not met yet.")
        else:
            print("Waiting for user command...")

        time.sleep(10) # Check happens every ~ 10 seconds


if __name__ == "__main__":
    main_loop()
