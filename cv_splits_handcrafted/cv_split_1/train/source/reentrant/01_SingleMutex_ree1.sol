
contract C {
    bool flag = false;
    mapping (address => uint256) public balances;

    function withdraw(uint256 amt) public {
        flag = true;

        require(balances[msg.sender] >= amt, "Insufficient funds");
        (bool success, ) = msg.sender.call{value:amt}("");
        require(success, "Call failed");
        balances[msg.sender] -= amt;

        flag = false;
    }

}
