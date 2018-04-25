#!/bin/sh

export LC_ALL=C.UTF-8
export LANG=C.UTF-8
export FLASK_APP=faucet.py

cd /root
./db-init.sh

python3 serve.py
