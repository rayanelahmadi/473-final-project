
from web3 import Web3
import os
from dotenv import load_dotenv
import time

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

RPC_URL = os.getenv("RPC_URL")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
PUBLIC_ADDRESS = os.getenv("PUBLIC_ADDRESS")

w3 = Web3(Web3.HTTPProvider(RPC_URL))

XRP_TOKEN = Web3.to_checksum_address("0xa13a7Ee21970FdA24d9B75b3178aaab658F93160")
WETH = Web3.to_checksum_address("0x0D0C9f562f36A6243133508d4E9aDC6873368BBE")
ROUTER = Web3.to_checksum_address("0x8DD9D609C6F1240AD1e69Ac8b0170D4eC845d773")

"""
# Standard ERC-20 ABI (simplified for transfer function)
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

token_contract = w3.eth.contract(address=XRP_TOKEN_ADDRESS, abi=ERC20_ABI)"""

# ✅ Router ABI (only needed functions)
ROUTER_ABI = [
    {
        "name": "swapExactETHForTokens",
        "type": "function",
        "stateMutability": "payable",
        "inputs": [
            {"name": "amountOutMin", "type": "uint256"},
            {"name": "path", "type": "address[]"},
            {"name": "to", "type": "address"},
            {"name": "deadline", "type": "uint256"}
        ],
        "outputs": [{"name": "amounts", "type": "uint256[]"}]
    }
]

router_contract = w3.eth.contract(address=ROUTER, abi=ROUTER_ABI)


def execute_trade(token_symbol="PEPE", amount=0.001):
    if not w3.is_connected():
        raise Exception("🚫 Web3 connection failed")
    if token_symbol.upper() != "XRP":
        print(f"❌ Unsupported token: {token_symbol}")
        return

    # Convert ETH to Wei
    #value = w3.to_wei(eth_amount, "ether")

     # 🧠 Set up swap parameters
    amountOutMin = 1  # Accept any amount of XRP for now (unsafe for mainnet)
    deadline = int(time.time()) + 120  # 2-minute timeout
    path = [WETH, XRP_TOKEN]

    # 🧾 Build transaction
    txn = router_contract.functions.swapExactETHForTokens(
        amountOutMin,
        path,
        PUBLIC_ADDRESS,
        deadline
    ).build_transaction({
        'from': PUBLIC_ADDRESS,
        'value': w3.to_wei(amount, "ether"),
        'gas': 300000,
        'gasPrice': w3.to_wei('10', 'gwei'),
        'nonce': w3.eth.get_transaction_count(PUBLIC_ADDRESS),
        'chainId': 11155111
    })

    # Convert to base units (18 decimals)
    token_amount = int(amount * 10**18)

    # Build transaction
    nonce = w3.eth.get_transaction_count(PUBLIC_ADDRESS)
    """
    tx = {
        'to': PUBLIC_ADDRESS,  # for now, just send to self (mock)
        'value': value,
        'gas': 21000,
        'gasPrice': w3.to_wei('10', 'gwei'),
        'nonce': nonce,
        'chainId': 11155111  # Sepolia chain ID
    }"""
    """
    tx = token_contract.functions.transfer(
        '0x70B4124E18DFe09C369a47136f848e77fcC579C4',  # send to yourself (demo)
        token_amount
    ).build_transaction({
        'from': PUBLIC_ADDRESS,
        'gas': 60000,
        'gasPrice': w3.to_wei('10', 'gwei'),
        'nonce': nonce,
        'chainId': 11155111
    })"""

    # Sign and send
    signed_txn = w3.eth.account.sign_transaction(txn, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)

    print(f"✅ Trade executed (mock buy {token_symbol}): https://sepolia.etherscan.io/tx/0x{tx_hash.hex()}")
    return tx_hash.hex()
