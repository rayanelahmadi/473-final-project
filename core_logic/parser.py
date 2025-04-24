import os
from dotenv import load_dotenv
from openai import OpenAI
import json


# Load .env from project root
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

#openai.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


GPT_SYSTEM_PROMPT = """
You are a helpful assistant that extracts structured data from user input.
The user will send natural language commands for DeFi trading, like:
"Buy $PEPE if it's trending and gas < 30 gwei"

Your job is to return a JSON object with the following fields:
- action: "buy" or "sell"
- token: string (ex: "PEPE")
- amount: number (default of 0.001 if not mentioned by user)
- conditions:
    - reddit_trending: true if mentioned
    - gas_price_threshold: number (optional)
Only include fields that are clearly stated.
Respond only with a valid JSON object.
"""

async def parse_command(user_input: str) -> dict:
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": GPT_SYSTEM_PROMPT},
                {"role": "user", "content": user_input}
            ],
            temperature=0.2
        )
        content = response.choices[0].message.content
        print("🔍 GPT Raw Response:")
        print(content)

         # Remove markdown code block if present
        if content.startswith("```json"):
            content = content.replace("```json", "").strip()
        if content.endswith("```"):
            content = content[:-3].strip()

        return json.loads(content)  # Safer than eval()
    except Exception as e:
        raise RuntimeError(f"GPT parsing failed: {e}")
