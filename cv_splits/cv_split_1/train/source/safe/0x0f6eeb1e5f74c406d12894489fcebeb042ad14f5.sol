contract owned {

    address public owner;

    constructor(address _owner) public {

        owner = _owner;

    }

    modifier onlyOwner {

        require(msg.sender == owner);

        _;

    }

    function transferOwnership(address newOwner) onlyOwner public {

        owner = newOwner; 

    } 

}

contract GOMIERC20 {

    string public name;

    string public symbol;

    uint8 public decimals = 0;

    uint256 public totalSupply;

    mapping (address => uint256) public balanceOf;

    event Transfer(address indexed from, address indexed to, uint256 value);

    event Burn(address indexed from, uint256 value);

    constructor(

        uint256 initialSupply,

        string memory tokenName,

        string memory tokenSymbol,

        address _owner

    ) public {

        totalSupply = initialSupply;  

        balanceOf[_owner] = totalSupply;                    

        name = tokenName;                                       

        symbol = tokenSymbol;                                   

    }

    function _transfer(address _from, address _to, uint _value) internal {

        require(_to != address(0x0));

        require(balanceOf[_from] >= _value);

        require(balanceOf[_to] + _value > balanceOf[_to]);

        uint previousBalances = balanceOf[_from] + balanceOf[_to];

        balanceOf[_from] -= _value;

        balanceOf[_to] += _value;

        emit Transfer(_from, _to, _value);

        assert(balanceOf[_from] + balanceOf[_to] == previousBalances);

    }

    function transfer(address _to, uint256 _value) public returns (bool success) {

        _transfer(msg.sender, _to, _value);

        return true;

    }

    function burn(uint256 _value) public returns (bool success) {

        require(balanceOf[msg.sender] >= _value);   

        balanceOf[msg.sender] -= _value;            

        totalSupply -= _value;                      

        emit Burn(msg.sender, _value);

        return true;

    }

}

contract GOMIToken is owned, GOMIERC20 {

    mapping (address => bool) public frozenAccount;

    event FrozenFunds(address target, bool frozen);

    constructor(

        uint256 initialSupply,

        string memory tokenName,

        string memory tokenSymbol,

        address _owner

     ) owned(_owner) GOMIERC20(initialSupply, tokenName, tokenSymbol,_owner) public {}

    function _transfer(address _from, address _to, uint _value) internal {

        require (_to != address(0x0));                          

        require (balanceOf[_from] >= _value);                   

        require (balanceOf[_to] + _value >= balanceOf[_to]);    

        require(!frozenAccount[_from]);                         

        require(!frozenAccount[_to]);                           

        balanceOf[_from] -= _value;                             

        balanceOf[_to] += _value;                               

        emit Transfer(_from, _to, _value);

    }

    function freezeAccount(address target, bool freeze) onlyOwner public {

        frozenAccount[target] = freeze;

        emit FrozenFunds(target, freeze);

    }

}
