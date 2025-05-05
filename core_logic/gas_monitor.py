import os
import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")

def get_current_gas_price() -> int:
    url = "https://api.etherscan.io/api"
    params = {
        "module": "gastracker",
        "action": "gasoracle",
        "apikey": ETHERSCAN_API_KEY
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        return float(data["result"]["ProposeGasPrice"])
    
    except Exception as e:
        print(f"Failed to fetch gas price: {e}")
        return -1  # use -1 as error fallback
