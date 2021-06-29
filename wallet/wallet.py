import subprocess
import json
from dotenv import load_dotenv
import os
from bit import PrivateKeyTestnet
from bit.network import NetworkAPI
from web3 import Account, middleware, Web3
from web3.gas_strategies.time_based import medium_gas_price_strategy
from web3.middleware import geth_poa_middleware


# Load and set environment variables
load_dotenv()
mnemonic=os.getenv("mnemonic")

# Import constants.py and necessary functions from bit and web3
from constants import *


w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

# Create a function called `derive_wallets`
def derive_wallets (mnemonic, coin):
    command = f'php hd-wallet-derive/hd-wallet-derive.php -g --mnemonic="{mnemonic}" --coin={coin} --cols=path,address,privkey,pubkey --format=json'
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    output, err = p.communicate()
    p_status = p.wait()
    return json.loads(output)
    

# Create a dictionary object called coins to store the output from `derive_wallets`.


coins = {ETH:[],BTCTEST:[]}


ethereum = derive_wallets(mnemonic, ETH)
btctest = derive_wallets(mnemonic, BTCTEST)
coins[ETH].append(ethereum[0:3])
coins[BTCTEST].append(btctest[0:3])


# Create a function called `priv_key_to_account` that converts privkey strings to account objects.
def priv_key_to_account(coin, priv_key):
    if coin == ETH:
        account = Account.privateKeyToAccount(priv_key)
    i:
        account = PrivateKeyTestnet(priv_key)

    return account


# Create a function called `create_tx` that creates an unsigned transaction appropriate metadata.
def create_tx(coin, account, to, amount):
    if coin == ETH:
        gasEstimate = w3.eth.estimateGas({"from": account.address, "to": to, "value": amount})
        return {"from": account.address,"to": to,"value": amount,"gasPrice": w3.eth.gasPrice,"gas": gasEstimate,"nonce": w3.eth.getTransactionCount(account.address),}
    else:
        return PrivateKeyTestnet.prepare_transaction(account.address, [(to, amount, BTC)])

# Create a function called `send_tx` that calls `create_tx`, signs and sends the transaction.
def send_tx(coin, account, to, amount):
    if coin == ETH:
        raw_tx = create_raw_tx(coin, account.address, to, amount)
        signed = account.sign_transaction(raw_tx)
        return w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    else:
        raw_tx = create_tx(coin, account, to, amount)
        signed = account.sign_transaction(raw_tx)
        return NetworkAPI.broadcast_tx_testnet(signed)
