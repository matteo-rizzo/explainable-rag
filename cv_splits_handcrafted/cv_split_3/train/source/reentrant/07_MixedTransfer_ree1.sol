
contract C {
    mapping (address => uint256) public balances;

    function withdraw(uint256 amt) public {
        require(balances[msg.sender] >= amt, "Insufficient funds");
        payable(msg.sender).transfer(amt);

        (bool success, ) = msg.sender.call{value:0}("");
        require(success, "Call failed");
        balances[msg.sender] -= amt;
    }

    function deposit() public payable {
        balances[msg.sender] += msg.value;       
    }

}
