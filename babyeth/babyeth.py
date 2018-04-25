#!/usr/bin/env python3

import time
import random
import sys
import string

from web3 import Web3, HTTPProvider, IPCProvider
from solc import compile_source
from web3.contract import ConciseContract

flag = 'flag{this_is_a_super_long_string_because_i_hope_you_script_this_out}'

def main():
    print('Connecting to geth')
    w3 = Web3(HTTPProvider('http://public-node:8545'))
    transaction, instance = get_instance(w3)
    print(flag)
    flagdict = dict()
    for index, char in enumerate(flag):
        flagdict[str(index)] = char
    keys = list(flagdict.keys())
    random.shuffle(keys)
    for i in keys:
        time.sleep(5)
        print('publishing: '+i+':'+flagdict[i])
        sys.stdout.flush()
        instance.genEvent(int(i), 'character: '+flagdict[i], transact=transaction)
        time.sleep(2)
        rand_str = lambda n: ''.join([random.choice(string.ascii_letters) for i in range(n)])
        instance.setFlag(rand_str(10), transact=transaction)

def get_instance(w3):
    contract_source = ''
    with open('babyeth.sol') as f:
        contract_source = f.read()

    print('Compiling sol')
    compiled_sol = compile_source(contract_source)
    interface = compiled_sol['<stdin>:Babyeth']

    cont_addr = ''
    with open('/root/shared/babyeth-contract.txt', 'r') as f:
        cont_addr = f.read().strip()
    transaction = {
        'value': 0,
        'to'   : cont_addr,
        'from' : w3.eth.coinbase,
        'gasPrice': w3.toWei(18, 'gwei'),
        'gas': 4100000
    }
    if not w3.personal.unlockAccount(w3.eth.coinbase, '420blaze69everysingle1337day'):
        print('Wrong account unlock passphrase... Quitting')
        exit(-1)
    instance = w3.eth.contract(abi=interface['abi'], address=cont_addr, \
            ContractFactoryClass=ConciseContract)
    return (transaction, instance)



main()
