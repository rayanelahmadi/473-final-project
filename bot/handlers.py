from telegram import Update
from telegram.ext import ContextTypes
from telegram import Bot
from core_logic.parser import parse_command
import json
import os

chat_id_file = "chat_id.txt"

def save_chat_id(chat_id):
    with open(chat_id_file, "w") as f:
        f.write(str(chat_id))


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    save_chat_id(update.message.chat_id)

    await update.message.reply_text("Parsing your command...")

    try:
        command_data = await parse_command(user_input)

        # Save to file
        with open("parsed_command.json", "w") as f:
            json.dump(command_data, f)
        response = f"Got it! Will let you know once trade is executed."

    except Exception as e:
        response = f"Failed to parse command: {e}"

    await update.message.reply_text(response) 
    


async def notify_user(message):
    with open("chat_id.txt", "r") as f:
        chat_id = f.read().strip()
    bot = Bot(token=os.getenv("TELEGRAM_API_KEY"))
    await bot.send_message(chat_id=chat_id, text=message)