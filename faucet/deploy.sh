#!/bin/bash

sh ./db-init.sh

screen -S "faucet" -d -m
sleep 0.1
screen -r "faucet" -X stuff $'python3 serve.py\n'
