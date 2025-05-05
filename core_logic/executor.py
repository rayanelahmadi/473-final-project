
from web3 import Web3
import os
from dotenv import load_dotenv
import time

from bot.handlers import notify_user
import asyncio

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

RPC_URL = os.getenv("RPC_URL")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
PUBLIC_ADDRESS = os.getenv("PUBLIC_ADDRESS")

w3 = Web3(Web3.HTTPProvider(RPC_URL))

XRP_TOKEN = Web3.to_checksum_address("0xBB5313B7d205267C1bAf8D41870B25c33BAaC4aB")
WETH = Web3.to_checksum_address("0x0D0C9f562f36A6243133508d4E9aDC6873368BBE")
ROUTER = Web3.to_checksum_address("0x6404DD2bB9587702786F36a843150D1BdeED0D0A")


# Standard ERC-20 ABI
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
    },
    {
        "constant": False,
        "inputs": [
            {"name": "spender", "type": "address"},
            {"name": "amount", "type": "uint256"}
        ],
        "name": "approve",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {"name": "from", "type": "address"},
            {"name": "to", "type": "address"},
            {"name": "value", "type": "uint256"}
        ],
        "name": "transferFrom",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function"
    }
]

token_contract = w3.eth.contract(address=XRP_TOKEN, abi=ERC20_ABI)


# Router ABI (only needed functions)
ROUTER_ABI = [
    {
        "inputs": [
        { "internalType": "uint256", "name": "amountOut", "type": "uint256" },
        { "internalType": "address[]", "name": "path", "type": "address[]" },
        { "internalType": "address", "name": "to", "type": "address" },
        { "internalType": "uint256", "name": "deadline", "type": "uint256" }
        ],
        "name": "swapETHForExactTokens",
        "outputs": [
        { "internalType": "uint256[]", "name": "amounts", "type": "uint256[]" }
        ],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [
        { "internalType": "uint256", "name": "amountIn", "type": "uint256" },
        { "internalType": "uint256", "name": "amountOutMin", "type": "uint256" },
        { "internalType": "address[]", "name": "path", "type": "address[]" },
        { "internalType": "address", "name": "to", "type": "address" },
        { "internalType": "uint256", "name": "deadline", "type": "uint256" }
        ],
        "name": "swapExactTokensForETH",
        "outputs": [
        { "internalType": "uint256[]", "name": "amounts", "type": "uint256[]" }
        ],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {"name": "from", "type": "address"},
            {"name": "to", "type": "address"},
            {"name": "value", "type": "uint256"}
        ],
        "name": "transferFrom",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function"
    }
]

router_contract = w3.eth.contract(address=ROUTER, abi=ROUTER_ABI)


def execute_trade(token_symbol="XRP", amount=0.001, buy=True):
    if not w3.is_connected():
        raise Exception("Web3 connection failed")
    if token_symbol.upper() != "XRP":
        print(f"Unsupported token: {token_symbol}")
        return

    # Perform buy action
    if buy:
        # Prepare arguments
        amountOut = amount * (10**18)  # amount XRP (assuming 18 decimals)
        path = [WETH, XRP_TOKEN]
        recipient = PUBLIC_ADDRESS
        deadline = int(time.time()) + 300  # 5 minutes from now

        # Calculate ETH required (1000 XRP @ 1 ETH due to constant ratio set in Router)
        required_eth = amountOut // 1000

        # Send transaction
        tx = router_contract.functions.swapETHForExactTokens(
            amountOut,
            path,
            recipient,
            deadline
        ).build_transaction({
            'from': PUBLIC_ADDRESS,
            'value': required_eth,
            'gas': 300000,
            'gasPrice': w3.to_wei('10', 'gwei'),
            'nonce': w3.eth.get_transaction_count(PUBLIC_ADDRESS),
            'chainId': 11155111
        })

    # Perform sell action
    else:
        # Approve router to spend XRP:
        amountIn = amount * (10**18)

        approve_tx = token_contract.functions.approve(
            ROUTER, amountIn
        ).build_transaction({
            'from': PUBLIC_ADDRESS,
            'gas': 100000,
            'gasPrice': w3.to_wei('10', 'gwei'),
            'nonce': w3.eth.get_transaction_count(PUBLIC_ADDRESS)
        })

        signed_approve = w3.eth.account.sign_transaction(approve_tx, PRIVATE_KEY)
        approve_hash = w3.eth.send_raw_transaction(signed_approve.raw_transaction)

        receipt = w3.eth.wait_for_transaction_receipt(approve_hash)
        if receipt['status'] != 1:
            print("Approval transaction failed!")
            return


        # Call swapExactTokensForETH
        amountOutMin = (amountIn // 1000)  # Should be same or less to account for something like slippage
        path = [XRP_TOKEN, WETH]
        deadline = int(time.time()) + 300

        tx = router_contract.functions.swapExactTokensForETH(
            amountIn,
            amountOutMin,
            path,
            PUBLIC_ADDRESS,
            deadline
        ).build_transaction({
            'from': PUBLIC_ADDRESS,
            'gas': 300000,
            'gasPrice': w3.to_wei('10', 'gwei'),
            'nonce': w3.eth.get_transaction_count(PUBLIC_ADDRESS) + 1
        })


    # Sign and send
    signed_txn = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)

    print(f"Trade executed (mock {token_symbol}): https://sepolia.etherscan.io/tx/0x{tx_hash.hex()}")
    asyncio.run(notify_user(f"Trade executed (mock {token_symbol}): https://sepolia.etherscan.io/tx/0x{tx_hash.hex()}"))
    return tx_hash.hex()
