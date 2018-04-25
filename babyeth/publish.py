#!/usr/bin/env python3

import json
import pdb
import web3
import time
import pickle
import sys

from web3 import Web3, HTTPProvider, IPCProvider
from solc import compile_source
from web3.contract import ConciseContract

print('Connecting to geth')
web3 = Web3(HTTPProvider('http://public-node:8545'))

contract_source = ''
with open('babyeth.sol') as f:
    contract_source = f.read()

print('Compiling sol')
compiled_sol = compile_source(contract_source)
interface = compiled_sol['<stdin>:Babyeth']

contract = web3.eth.contract(abi=interface['abi'], bytecode=interface['bin'])

with open('babyeth.abi', 'wb+') as f:
    pickle.dump(interface['abi'], f)

if not web3.personal.unlockAccount(web3.eth.coinbase, '420blaze69everysingle1337day'):
    print('Wrong account unlock passphrase... Quitting')
    exit(-1)

print('Waiting for funds to be available.........')
sys.stdout.flush()
while web3.eth.getBalance(web3.eth.coinbase) == 0:
    time.sleep(1)
time.sleep(1)
print('Deploying contract...')
args = ['somerandomstring']
transaction = {'from': web3.eth.accounts[0]}
tx_hash = contract.deploy(transaction=transaction, args=args)

print('\n======INFO=====')
print('TX hash: {}'.format(str(tx_hash)))
print('Waiting for TX to be mined (2 blocks).........')
sys.stdout.flush()
block = web3.eth.blockNumber
while web3.eth.blockNumber != block+2:
    time.sleep(1)
time.sleep(1)
tx_receipt = web3.eth.getTransactionReceipt(tx_hash)
contract_address = tx_receipt['contractAddress']
print('Contract address: {}'.format(str(contract_address)))
print('======INFO=====')

with open('/root/shared/babyeth-contract.txt', 'w+') as f:
    f.write(str(contract_address)+'\n')
