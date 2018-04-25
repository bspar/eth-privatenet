window.addEventListener('load', function() {
    var Web3 = require('web3')
    if (typeof Web3 !== 'undefined') {
        window.web3 = new Web3(web3.currentProvider);
    } else {
        console.log('No web3, please install MetaMask');
        return;
    }

    web3.version.getNetwork((err, netId) => {
        if (netId != '133742069') {
            console.log('Please connect to the CTF blockchain');
            return;
        }
    });

    try {
        web3.eth.getBalance(web3.eth.accounts[0], (error, result) => {
            if (result == 0) {
                console.log('You have no coin!');
                console.log('Ask your captain for coin, or make sure your address is '+
                    'correct on your scoreboard account');
            }
        });
    } catch (e) {
        console.log('Metamask is a pretty UI for basic ETH interaction');
    }
})

function sendcoin(ether, receiver) {
    transaction = {
        from: web3.eth.accounts[0],
        to: receiver,
        value: web3.toWei(ether, 'ether'),
        gasPrice: web3.toWei('18', 'gwei')
    };
    web3.eth.sendTransaction(transaction, (err, transactionHash) => {
        if (!err) console.log(transactionHash);
        else console.log(err);
    });
}
