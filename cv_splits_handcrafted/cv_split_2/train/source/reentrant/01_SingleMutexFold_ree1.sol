
contract C {
    bool flag = false;
    mapping (address => uint256) public balances;

    function toggle() internal {
        flag = !flag;
    }

    function withdraw(uint256 amt) public {
        require(!flag, "Locked");

        require(balances[msg.sender] >= amt, "Insufficient funds");
        (bool success, ) = msg.sender.call{value:amt}("");
        require(success, "Call failed");
        balances[msg.sender] -= amt;

        toggle();
    }

    function deposit() public payable {
        balances[msg.sender] += msg.value;       
    }

}
