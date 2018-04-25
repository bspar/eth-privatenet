#!/bin/sh

sleep 1
geth --datadir /root/.ethereum/c3tfnet --networkid 133742069 init /root/shared/c3tfnet.json
geth --datadir /root/.ethereum/c3tfnet --networkid 133742069 --nodiscover --rpc --rpcport 8545 --rpcaddr 0.0.0.0 --rpccorsdomain "*" --rpcvhosts "*" --rpcapi admin,eth,net,personal,web3,txpool &

sleep 3
NODEID=$(cat /root/shared/poa-nodeid | tr -d '\n')
NODEIP=$(getent hosts poa-node | awk '{ print $1 }' | tr -d '\n')
ENODE="enode://$NODEID@$NODEIP:30303?discport=0"
geth --datadir /root/.ethereum/c3tfnet attach ipc:/root/.ethereum/c3tfnet/geth.ipc --exec "admin.addPeer(\"$ENODE\")"

wait
