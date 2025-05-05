from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

RPC_URL = os.getenv("RPC_URL")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
PUBLIC_ADDRESS = os.getenv("PUBLIC_ADDRESS")

w3 = Web3(Web3.HTTPProvider(RPC_URL))

XRP_TOKEN = Web3.to_checksum_address("0xBB5313B7d205267C1bAf8D41870B25c33BAaC4aB")

ROUTER_ADDRESS = Web3.to_checksum_address("0x6404DD2bB9587702786F36a843150D1BdeED0D0A")

# ERC-20 ABI with just transfer function
ERC20_ABI = [
    {
        "constant": False,
        "inputs": [
            {"name": "to", "type": "address"},
            {"name": "value", "type": "uint256"}
        ],
        "name": "transfer",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function"
    }
]

token_contract = w3.eth.contract(address=XRP_TOKEN, abi=ERC20_ABI)

def fund_router_with_xrp(amount_xrp: float):
    if not w3.is_connected():
        raise Exception("Web3 connection failed")

    # assumes 18 decimals
    amount = int(amount_xrp * 10**18)

    # Complete transaction
    nonce = w3.eth.get_transaction_count(PUBLIC_ADDRESS)
    tx = token_contract.functions.transfer(
        ROUTER_ADDRESS,
        amount
    ).build_transaction({
        'from': PUBLIC_ADDRESS,
        'gas': 60000,
        'gasPrice': w3.to_wei('10', 'gwei'),
        'nonce': nonce,
        'chainId': 11155111  # Sepolia ID
    })

    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

    print(f"Sent {amount_xrp} XRP to Router. TX: https://sepolia.etherscan.io/tx/0x{tx_hash.hex()}")
    return tx_hash.hex()

# Example: fund with 1000 XRP
fund_router_with_xrp(1000)
