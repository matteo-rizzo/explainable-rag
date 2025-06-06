
contract C {
    mapping (address => uint256) public balances;

    function pay(uint256 amt) internal {
        (bool success, ) = msg.sender.call{value:amt}("");
        require(success, "Call failed");
    }

    function withdraw(uint256 amt) public {
        require(balances[msg.sender] >= amt, "Insufficient funds");
        pay(amt);
        balances[msg.sender] -= amt;
    }

    function deposit() public payable {
        balances[msg.sender] += msg.value;       
    }

}
