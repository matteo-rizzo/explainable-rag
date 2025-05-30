interface IERC20 {

    function totalSupply() external view returns (uint256);

    function balanceOf(address who) external view returns (uint256);

    function allowance(address owner, address spender) external view returns (uint256);

    function transfer(address to, uint256 value) external returns (bool);

    function approve(address spender, uint256 value) external returns (bool);

    function transferFrom(address from, address to, uint256 value) external returns (bool);

    event Transfer(address indexed from, address indexed to, uint256 value);

    event Approval(address indexed owner, address indexed spender, uint256 value);

}

library SafeMath {

    function mul(uint256 a, uint256 b) internal pure returns (uint256) {

        if (a == 0) {

            return 0;

        }

        uint256 c = a * b;

        require(c / a == b);

        return c;

    }

    function div(uint256 a, uint256 b) internal pure returns (uint256) {

        require(b > 0);

        uint256 c = a / b;

        return c;

    }

    function sub(uint256 a, uint256 b) internal pure returns (uint256) {

        require(b <= a);

        uint256 c = a - b;

        return c;

    }

    function add(uint256 a, uint256 b) internal pure returns (uint256) {

        uint256 c = a + b;

        require(c >= a);

        return c;

    }

    function mod(uint256 a, uint256 b) internal pure returns (uint256) {

        require(b != 0);

        return a % b;

    }

}

library Roles {

    struct Role {

        mapping (address => bool) bearer;

    }

    function add(Role storage role, address account) internal {

        require(account != address(0));

        require(!has(role, account));

        role.bearer[account] = true;

    }

    function remove(Role storage role, address account) internal {

        require(account != address(0));

        require(has(role, account));

        role.bearer[account] = false;

    }

    function has(Role storage role, address account) internal view returns (bool) {

        require(account != address(0));

        return role.bearer[account];

    }

}

contract VIDERC20 is IERC20, Ownable {

    using SafeMath for uint256;

    mapping (address => uint256) private _balances;

    mapping (address => mapping (address => uint256)) private _allowed;

    uint256 public sellPrice;

    uint256 public buyPrice;

    string public name = "VID";

    string public symbol = "VID";

    uint8 public decimals = 5;

    uint256 private _totalSupply;

    uint256 public constant initialSupply = 62500000000000;

    constructor () public {

          _totalSupply = initialSupply;

          _balances[msg.sender] = initialSupply;

    }

    function totalSupply() public view returns (uint256) {

        return _totalSupply;

    }

    function balanceOf(address owner) public view returns (uint256) {

        return _balances[owner];

    }

    function allowance(address owner, address spender) public view returns (uint256) {

        return _allowed[owner][spender];

    }

    function transfer(address to, uint256 value) public returns (bool) {

        _transfer(msg.sender, to, value);

        return true;

    }

    function approve(address spender, uint256 value) public returns (bool) {

        require(spender != address(0));

        _allowed[msg.sender][spender] = value;

        emit Approval(msg.sender, spender, value);

        return true;

    }

    function transferFrom(address from, address to, uint256 value) public returns (bool) {

        _allowed[from][msg.sender] = _allowed[from][msg.sender].sub(value);

        _transfer(from, to, value);

        emit Approval(from, msg.sender, _allowed[from][msg.sender]);

        return true;

    }

    function _transfer(address from, address to, uint256 value) internal {

        require(to != address(0));

        _balances[from] = _balances[from].sub(value);

        _balances[to] = _balances[to].add(value);

        emit Transfer(from, to, value);

    }

}
