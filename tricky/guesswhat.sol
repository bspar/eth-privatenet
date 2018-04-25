pragma solidity ^0.4.16;

contract Guesswhat {
    string public name;
    bytes32 public sha_secret;
    string public flag;
    bytes32 public challenge_hash;

    event NewGuess(bytes32 challenge);
    event ContractUpgrade(address newcontract);

    function Guesswhat(string secret) public {
        sha_secret = keccak256(secret);
        flag = "Nope";
    }

    function publishChallenge(bytes32 secret, bytes32 challenge) public {
        require(secret == sha_secret);
        challenge_hash = challenge;
    }

    function getChallenge() public returns (bytes32) {
        return challenge_hash;
    }

    function guessAnswer(bytes32 guess) public {
        require(keccak256(guess) == challenge_hash);
        // binary assumes 32 bytes, but new contract can change type
        // since arg 'challenge' is non-indexed, it'll plop in 'data'
        // along with any other args that the new contract has
        NewGuess(guess);
    }

    function setFlag(string newflag) public {
        flag = newflag;
    }

    function getFlag() public returns (string) {
        return flag;
    }

    // Steal contract pls
    function upgrade(bytes32 secret, address newcontract) public {
        require(secret == sha_secret);
        ContractUpgrade(newcontract);
    }
}
