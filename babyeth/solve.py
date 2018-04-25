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
with open('babyeth.sol') as f:
    contract_source = f.read()

print('Compiling sol')
compiled_sol = compile_source(contract_source)
interface = compiled_sol['<stdin>:Babyeth']

cont_addr = '0x9f59D5f7235A0036197325E406002Df2324744Bd'
instance = w3.eth.contract(abi=interface['abi'], address=cont_addr, \
        ContractFactoryClass=Contract)

event_filter = w3.eth.filter({
    # 'address':cont_addr,
    'fromBlock' : '0x1',
    'toBlock' : 'latest',
    'topics' : ['0x48082e5794032e44b2c7bf06b0c74a700960e33cc59fcd6351fad5fa121ae547']
})

flagdict = dict()
# for x in range(0,15):
logs = event_filter.get_all_entries()
for log in logs:
    flagdict[log['data'][2:66]] = chr(int('0x'+log['data'][216:218], 16))
flag = []
for key in sorted(flagdict.keys()):
    flag.append(flagdict[key])
print(''.join(flag))

pdb.set_trace()
