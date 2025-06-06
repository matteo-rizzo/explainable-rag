contract SimpleDAO {
    mapping(address => uint) public credit;
    bool public flag;
    bytes data;

    function donate(address to) public payable {
        credit[to] += msg.value;
    }

    function withdraw(uint amount) public {
        if (credit[msg.sender] >= amount) {

            (flag, data) = msg.sender.call.value(amount)("");
            if (flag == true) {
                credit[msg.sender] -= amount;
            }
        }
    }

    function queryCredit(address to) public view returns (uint) {
        return credit[to];
    }
}
