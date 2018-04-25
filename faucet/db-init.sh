#!/bin/bash

export FLASK_APP=faucet.py
export FLASK_DEBUG=1
flask db init
mkdir tmp
flask db migrate
flask db upgrade

