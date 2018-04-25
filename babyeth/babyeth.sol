pragma solidity ^0.4.16;

contract Babyeth {
    string public name;
    string public bla;

    event SomeEvent(int index, string secret);

    function Babyeth(string secret) public {
        bla = "Nope";
    }

    function genEvent(int index, string secret) public {
        SomeEvent(index, secret);
    }

    function setFlag(string newbla) public {
        bla = newbla;
    }

    function getFlag() public returns (string) {
        return bla;
    }
}
