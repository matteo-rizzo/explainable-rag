
contract C {
    bool flag = false;
    mapping (address => uint256) public balances;

    modifier nonReentrant() {
        flag = true;
        _;
        flag = false;
    }

    function withdraw(uint256 amt) nonReentrant public {
        require(balances[msg.sender] >= amt, "Insufficient funds");
        (bool success, ) = msg.sender.call{value:amt}("");
        require(success, "Call failed");
        balances[msg.sender] -= amt;
    }

    function deposit() public payable {
        balances[msg.sender] += msg.value;       
    }

}
