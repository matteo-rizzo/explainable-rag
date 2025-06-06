contract WGOVM {
    function transferFrom(address _from,address _to,uint256 _value) public  returns (bool) ;
    function mint(address _to, uint256 _amount, bytes32 _trans) public returns (bool);
    function burn(uint256 _value, bytes memory _addr) public;
    function transferOwnership(address newOwner) public;
    function allowance(address _owner, address _spender)public view returns (uint256);
}

library ECDSA {
    function recover(bytes32 hash, bytes memory signature)
        internal
        pure
        returns (address)
    {

        if (signature.length != 65) {
            revert("ECDSA: invalid signature length");
        }

        bytes32 r;
        bytes32 s;
        uint8 v;

        assembly {
            r := mload(add(signature, 0x20))
            s := mload(add(signature, 0x40))
            v := byte(0, mload(add(signature, 0x60)))
        }

        if (
            uint256(s) >
            0x7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF5D576E7357A4501DDFE92F46681B20A0
        ) {
            revert("ECDSA: invalid signature 's' value");
        }

        if (v != 27 && v != 28) {
            revert("ECDSA: invalid signature 'v' value");
        }

        address signer = ecrecover(hash, v, r, s);
        require(signer != address(0), "ECDSA: invalid signature");

        return signer;
    }

    function toEthSignedMessageHash(bytes32 hash)
        internal
        pure
        returns (bytes32)
    {

        return
            keccak256(
                abi.encodePacked("\x19Ethereum Signed Message:\n32", hash)
            );
    }
}

contract Manager {
    using ECDSA for bytes32;
    address public owner;
    address public app = 0xaC5d7dFF150B195C97Fca77001f8AD596eda1761;
    WGOVM govm = WGOVM(app);

    event NeedApprove(address indexed from, address indexed to, uint256 value);

    constructor() public {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == owner);
        _;
    }

    function relayMint(
        address _to,
        uint256 _amount,
        bytes32 _trans,
        bytes memory approvalData
    ) public returns (bool) {
        bytes memory blob = abi.encodePacked(_to, _amount, _trans);
        address who = keccak256(blob).toEthSignedMessageHash().recover(approvalData);
        require(who == owner);
        return govm.mint(_to, _amount, _trans);
    }

    function burn(uint256 _value, bytes memory _addr) public returns (bool) {
        require(_value > 0);
        if (govm.allowance(msg.sender,address(this)) < _value){
            emit NeedApprove(msg.sender,address(this),_value);
            return false;
        }
        govm.transferFrom(msg.sender,address(this),_value);
        govm.burn(_value, _addr);
        return true;
    }

    function mint(address _to,uint256 _amount, bytes32 _trans)public onlyOwner returns (bool){
        return govm.mint(_to, _amount, _trans);
    }

    function transferAppOwnership() public onlyOwner {
        govm.transferOwnership(owner);
    }
}
