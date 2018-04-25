#!/bin/sh

geth account new --datadir /root/.ethereum/c3tfnet --password /root/.ethereum/c3tfnet.pass
sed -i -e "s/POAADDRESS/$(geth account list --datadir /root/.ethereum/c3tfnet 2>/dev/null | awk -F'[{}]' '{print $2}')/g" /root/.ethereum/c3tfnet.json
cp /root/.ethereum/c3tfnet.json /root/shared/c3tfnet.json
geth --datadir /root/.ethereum/c3tfnet --networkid 133742069 init /root/shared/c3tfnet.json
geth --datadir /root/.ethereum/c3tfnet --networkid 133742069 --nodiscover &

sleep 2
geth --datadir /root/.ethereum/c3tfnet attach ipc:/root/.ethereum/c3tfnet/geth.ipc --exec 'admin.nodeInfo.id' | tr -d '"' > /root/shared/poa-nodeid
geth --datadir /root/.ethereum/c3tfnet attach ipc:/root/.ethereum/c3tfnet/geth.ipc --exec 'personal.unlockAccount(eth.coinbase, "meowmeow", 0)'
geth --datadir /root/.ethereum/c3tfnet attach ipc:/root/.ethereum/c3tfnet/geth.ipc --exec 'miner.start(1)'

sleep 10
for i in `seq 1 10`;
do
    sleep 1
    if [ -e /root/shared/guess.txt ]
    then
        WALLET=$(cat /root/shared/guess.txt)
        geth --datadir /root/.ethereum/c3tfnet attach ipc:/root/.ethereum/c3tfnet/geth.ipc --exec "eth.sendTransaction({from:eth.coinbase, to:\"$WALLET\", value:web3.toWei(10000, 'ether')})"
        mv /root/shared/guess.txt /root/shared/account.txt
    fi
    if [ -e /root/shared/babyeth.txt ]
    then
        WALLET=$(cat /root/shared/babyeth.txt)
        geth --datadir /root/.ethereum/c3tfnet attach ipc:/root/.ethereum/c3tfnet/geth.ipc --exec "eth.sendTransaction({from:eth.coinbase, to:\"$WALLET\", value:web3.toWei(10000, 'ether')})"
        mv /root/shared/babyeth.txt /root/shared/babyeth-account.txt
    fi
done

wait
