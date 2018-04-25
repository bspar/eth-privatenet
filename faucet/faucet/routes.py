import uuid
import web3
from web3 import Web3, HTTPProvider, IPCProvider
from flask import render_template, send_from_directory, request, make_response, \
    redirect
from faucet import app, db
from faucet.models import Session
from random import randint
from datetime import datetime, timedelta

@app.route('/')
def index():
    response = make_response(render_template('getcash.html', title='Faucet'))
    return response

@app.route('/req100', methods=['POST'])
def req100():
    address = request.form['address']
    if app.config['WEB3_PROVIDER'] == 'ipc':
        web3 = Web3(IPCProvider(app.config['WEB3_URI']))
    elif app.config['WEB3_PROVIDER'] == 'http':
        web3 = Web3(HTTPProvider(app.config['WEB3_URI']))
    else:
        return 'WEB3_PROVIDER not valid'

    session = Session.query.filter_by(reqamt=100).first()
    if session:
        return 'NOPE'
    session = Session(reqamt=100, address=address)
    db.session.add(session)
    db.session.commit()
    web3.personal.unlockAccount(web3.eth.coinbase, '420blaze69everysingle1337day')
    transaction = {
        'from' : web3.eth.coinbase,
        'to' : address,
        'value' : web3.toWei(100, 'ether'),
        'gasPrice' : web3.toWei(18, 'gwei'),
    }
    txid = web3.eth.sendTransaction(transaction)
    return 'Transaction: {}'.format(str(txid))


@app.route('/req', methods=['POST'])
def req():
    address = request.form['address']
    if app.config['WEB3_PROVIDER'] == 'ipc':
        web3 = Web3(IPCProvider(app.config['WEB3_URI']))
    elif app.config['WEB3_PROVIDER'] == 'http':
        web3 = Web3(HTTPProvider(app.config['WEB3_URI']))
    else:
        return 'WEB3_PROVIDER not valid'

    session = Session.query.order_by('reqtime desc').limit(1).one()
    if session.reqtime+timedelta(minutes=5) > datetime.utcnow():
        return 'NOPE'
    session = Session(reqamt=100, address=address)
    db.session.add(session)
    db.session.commit()
    web3.personal.unlockAccount(web3.eth.coinbase, '420blaze69everysingle1337day')
    transaction = {
        'from' : web3.eth.coinbase,
        'to' : address,
        'value' : web3.toWei(1, 'ether'),
        'gasPrice' : web3.toWei(18, 'gwei'),
    }
    txid = web3.eth.sendTransaction(transaction)
    return 'Transaction: {}'.format(str(txid))

# static routes, probably better to serve over nginx/apache or soemthing
@app.route('/static/<name>')
def serve_static(name):
    return send_from_directory('static', name)
