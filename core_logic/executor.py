
from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

RPC_URL = os.getenv("RPC_URL")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
PUBLIC_ADDRESS = os.getenv("PUBLIC_ADDRESS")

w3 = Web3(Web3.HTTPProvider(RPC_URL))

def execute_trade(token_symbol="PEPE", eth_amount=0.001):
    if not w3.is_connected():
        raise Exception("🚫 Web3 connection failed")

    # Convert ETH to Wei
    value = w3.to_wei(eth_amount, "ether")

    # Build transaction
    nonce = w3.eth.get_transaction_count(PUBLIC_ADDRESS)
    tx = {
        'to': PUBLIC_ADDRESS,  # for now, just send to self (mock)
        'value': value,
        'gas': 21000,
        'gasPrice': w3.to_wei('10', 'gwei'),
        'nonce': nonce,
        'chainId': 11155111  # Sepolia chain ID
    }

    # Sign and send
    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

    print(f"✅ Trade executed (mock buy {token_symbol}): https://sepolia.etherscan.io/tx/0x{tx_hash.hex()}")
    return tx_hash.hex()
