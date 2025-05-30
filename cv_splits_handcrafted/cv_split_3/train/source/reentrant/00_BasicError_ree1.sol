
contract C {
    mapping (address => uint256) public balances;

    error InsufficientFunds(address caller, uint256 amt);

    function withdraw(uint256 amt) public {
        if(balances[msg.sender] < amt)
            revert InsufficientFunds(msg.sender, amt);
        (bool success, ) = msg.sender.call{value:amt}("");
        require(success, "Call failed");
        balances[msg.sender] -= amt;
    }

    function deposit() public payable {
        balances[msg.sender] += msg.value;       
    }

}
