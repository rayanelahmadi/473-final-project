from telegram import Update
from telegram.ext import ContextTypes
from core_logic.parser import parse_command
import json

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    #user_id = update.effective_user.id

    await update.message.reply_text("🤖 Parsing your command...")

    try:
        command_data = await parse_command(user_input)
        #state.latest_command = command_data # Save it globally
        #print(state.latest_command)
        # Save to file
        with open("parsed_command.json", "w") as f:
            json.dump(command_data, f)
        response = f"✅ Parsed command:\n{command_data}"
    except Exception as e:
        response = f"❌ Failed to parse command: {e}"

    await update.message.reply_text(response) # replace with response with an actual response user wants to see -> "Got it, will notify once trade executed!"
