interface IERC20 {

    function transfer(address to, uint256 value) external returns (bool);

    function approve(address spender, uint256 value) external returns (bool);

    function transferFrom(address from, address to, uint256 value) external returns (bool);

    function totalSupply() external view returns (uint256);

    function balanceOf(address who) external view returns (uint256);

    function allowance(address owner, address spender) external view returns (uint256);

    event Transfer(address indexed from, address indexed to, uint256 value);

    event Approval(address indexed owner, address indexed spender, uint256 value);

}

contract SafeMath {

  function safeMul(uint256 a, uint256 b) internal pure returns (uint256) {

    uint256 c = a * b;

    assert(a == 0 || c / a == b);

    return c;

  }

  function safeDiv(uint256 a, uint256 b) internal pure returns (uint256) {

    assert(b > 0);

    uint256 c = a / b;

    assert(a == b * c + a % b);

    return c;

  }

  function safeSub(uint256 a, uint256 b) internal pure returns (uint256) {

    assert(b <= a);

    return a - b;

  }

  function safeAdd(uint256 a, uint256 b) internal pure returns (uint256) {

    uint256 c = a + b;

    assert(c>=a && c>=b);

    return c;

  }

}

contract SpotChainToken is Ownable, SafeMath, IERC20{

    string public name;

    string public symbol;

    uint8 public decimals;

    uint256 public totalSupply;

    mapping (address => uint256) public balanceOf;

    mapping (address => mapping (address => uint256)) public allowance;

    mapping (address => bool) public frozenAccount;

    event Transfer(address indexed from, address indexed to, uint256 value);

    event Approval(address indexed owner, address indexed spender, uint256 value);

    event Burn(address indexed from, uint256 value);

    event FrozenFunds(address target, bool frozen);

    constructor()  public  {

        balanceOf[msg.sender] = 600000000000000000000000000;

        totalSupply = 600000000000000000000000000;

        name = "SpotChain Token";

        symbol = "GSB";

        decimals = 18;

    }

    function transfer(address _to, uint256 _value) public returns (bool) {

        require(!frozenAccount[msg.sender]);

        require(_to != address(0));

		require(_value > 0); 

        require(balanceOf[msg.sender] >= _value);

        require(balanceOf[_to] + _value >= balanceOf[_to]);

		uint previousBalances = balanceOf[msg.sender] + balanceOf[_to];		

        balanceOf[msg.sender] = SafeMath.safeSub(balanceOf[msg.sender], _value);

        balanceOf[_to] = SafeMath.safeAdd(balanceOf[_to], _value);

        emit Transfer(msg.sender, _to, _value);

		assert(balanceOf[msg.sender]+balanceOf[_to]==previousBalances);

        return true;

    }

    function approve(address _spender, uint256 _value) public returns (bool success) {

		require((_value == 0) || (allowance[msg.sender][_spender] == 0));

        allowance[msg.sender][_spender] = _value;

        emit Approval(msg.sender, _spender, _value);

        return true;

    }

    function transferFrom(address _from, address _to, uint256 _value) public returns (bool success) {

        require (_to != address(0));

		require (_value > 0); 

        require (balanceOf[_from] >= _value) ;

        require (balanceOf[_to] + _value > balanceOf[_to]);

        require (_value <= allowance[_from][msg.sender]);

        balanceOf[_from] = SafeMath.safeSub(balanceOf[_from], _value);

        balanceOf[_to] = SafeMath.safeAdd(balanceOf[_to], _value);

        allowance[_from][msg.sender] = SafeMath.safeSub(allowance[_from][msg.sender], _value);

        emit Transfer(_from, _to, _value);

        return true;

    }

     function burn(uint256 _value) public returns (bool success) {

        require(balanceOf[msg.sender] >= _value);   

        balanceOf[msg.sender] -= _value;            

        totalSupply -= _value;                      

        emit Burn(msg.sender, _value);

        return true;

    }

    function burnFrom(address _from, uint256 _value) public returns (bool success) {

        require(balanceOf[_from] >= _value);                

        require(_value <= allowance[_from][msg.sender]);    

        balanceOf[_from] -= _value;                         

        allowance[_from][msg.sender] -= _value;             

        totalSupply -= _value;                              

        emit Burn(_from, _value);

        return true;

    }

    function mintToken(address target, uint256 mintedAmount) onlyOwner public {

        balanceOf[target] += mintedAmount;

        totalSupply += mintedAmount;

        emit Transfer(address(0), address(this), mintedAmount);

        emit Transfer(address(this), target, mintedAmount);

    }

    function freezeAccount(address target, bool freeze) onlyOwner public {

        frozenAccount[target] = freeze;

        emit FrozenFunds(target, freeze);

    }

}
