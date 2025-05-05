from web3 import Web3
from dotenv import load_dotenv
import os

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

RPC_URL = os.getenv("RPC_URL")

w3 = Web3(Web3.HTTPProvider(RPC_URL))
XRP_TOKEN = Web3.to_checksum_address("0xBB5313B7d205267C1bAf8D41870B25c33BAaC4aB")
ROUTER_ADDRESS = Web3.to_checksum_address("0x6404DD2bB9587702786F36a843150D1BdeED0D0A")


ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "account", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function"
    }
]

xrp_contract = w3.eth.contract(address=XRP_TOKEN, abi=ERC20_ABI)

balance = xrp_contract.functions.balanceOf(ROUTER_ADDRESS).call()
print(f"Router XRP balance: {balance / 1e18} XRP")  # 18 decimals assumption
