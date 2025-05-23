library SafeMath {

    function mul(uint256 a, uint256 b) internal pure returns (uint256 c) {

        if (a == 0) {
            return 0;
        }

        c = a * b;
        assert(c / a == b);
        return c;
    }

    function div(uint256 a, uint256 b) internal pure returns (uint256) {

        return a / b;
    }

    function sub(uint256 a, uint256 b) internal pure returns (uint256) {
        assert(b <= a);
        return a - b;
    }

    function add(uint256 a, uint256 b) internal pure returns (uint256 c) {
        c = a + b;
        assert(c >= a);
        return c;
    }
}

contract ERC20Basic {
    function totalSupply() public view returns (uint256);
    function balanceOf(address who) public view returns (uint256);
    function transfer(address to, uint256 value) public returns (bool);
    event Transfer(address indexed from, address indexed to, uint256 value);
}

contract ERC20 is ERC20Basic {
    function allowance(
        address owner,
        address spender
    ) public view returns (uint256);

    function transferFrom(
        address from,
        address to,
        uint256 value
    ) public returns (bool);

    function approve(address spender, uint256 value) public returns (bool);
    event Approval(
        address indexed owner,
        address indexed spender,
        uint256 value
    );
}

library SafeERC20 {
    function safeTransfer(
        ERC20Basic token,
        address to,
        uint256 value
    ) internal {
        require(token.transfer(to, value));
    }

    function safeTransferFrom(
        ERC20 token,
        address from,
        address to,
        uint256 value
    ) internal {
        require(token.transferFrom(from, to, value));
    }

    function safeApprove(ERC20 token, address spender, uint256 value) internal {
        require(token.approve(spender, value));
    }
}

contract SpecialERC20 {
    function transfer(address to, uint256 value) public;
}

contract DecentralizedExchanges {
    using SafeMath for uint;
    using SafeERC20 for ERC20;

    string public name = "DecentralizedExchanges";

    event Order(bytes32 hash);
    event Trade(
        bytes32 hash,
        address seller,
        address token,
        uint amount,
        address purchaser,
        uint eth
    );
    event Cancel(bytes32 hash, uint amount, bool isSell);

    struct OrderInfo {
        bool isSell;
        bool isSpecialERC20;
        uint eth;
        uint amount;
        uint expires;
        uint nonce;
        uint createdAt;
        uint fill;
        address token;
        address[] limitUser;
        address owner;
    }

    mapping(bytes32 => OrderInfo) public orderInfos;
    mapping(address => bytes32[]) public userOrders;

    function getOrderInfo(
        bytes32 hash
    )
        public
        view
        returns (
            bool,
            uint,
            address,
            uint,
            uint,
            uint,
            address[],
            uint,
            address,
            uint,
            bool
        )
    {
        OrderInfo storage info = orderInfos[hash];
        return (
            info.isSell,
            info.eth,
            info.token,
            info.amount,
            info.expires,
            info.nonce,
            info.limitUser,
            info.createdAt,
            info.owner,
            info.fill,
            info.isSpecialERC20
        );
    }

    function createPurchaseOrder(
        bool isSpecialERC20,
        uint eth,
        address token,
        uint amount,
        uint expires,
        address[] seller,
        uint nonce
    ) public payable {
        require(msg.value >= eth);
        bytes32 hash = sha256(
            abi.encodePacked(
                this,
                eth,
                token,
                amount,
                expires,
                seller,
                nonce,
                msg.sender,
                now
            )
        );
        orderInfos[hash] = OrderInfo(
            false,
            isSpecialERC20,
            eth,
            amount,
            expires,
            nonce,
            now,
            0,
            token,
            seller,
            msg.sender
        );
        for (uint i = 0; i < userOrders[msg.sender].length; i++) {
            require(userOrders[msg.sender][i] != hash);
        }
        userOrders[msg.sender].push(hash);
        emit Order(hash);
    }

    function createSellOrder(
        bool isSpecialERC20,
        address token,
        uint amount,
        uint eth,
        uint expires,
        address[] purchaser,
        uint nonce
    ) public {
        ERC20(token).safeTransferFrom(msg.sender, this, amount);
        bytes32 hash = sha256(
            abi.encodePacked(
                this,
                eth,
                token,
                amount,
                expires,
                purchaser,
                nonce,
                msg.sender,
                now
            )
        );
        orderInfos[hash] = OrderInfo(
            true,
            isSpecialERC20,
            eth,
            amount,
            expires,
            nonce,
            now,
            0,
            token,
            purchaser,
            msg.sender
        );
        for (uint i = 0; i < userOrders[msg.sender].length; i++) {
            require(userOrders[msg.sender][i] != hash);
        }
        userOrders[msg.sender].push(hash);
        emit Order(hash);
    }

    function cancelOrder(bytes32 hash) public {
        OrderInfo storage info = orderInfos[hash];
        require(info.owner == msg.sender);
        if (info.isSell) {
            if (info.fill < info.amount) {
                uint amount = info.amount;
                uint remain = amount - info.fill;
                info.fill = info.amount;
                if (info.isSpecialERC20) {
                    SpecialERC20(info.token).transfer(msg.sender, remain);
                } else {
                    ERC20(info.token).transfer(msg.sender, remain);
                }
                emit Cancel(hash, remain, info.isSell);
            } else {
                emit Cancel(hash, 0, info.isSell);
            }
        } else {
            if (info.fill < info.eth) {
                uint eth = info.eth;
                remain = eth - info.fill;
                info.fill = info.eth;
                msg.sender.transfer(eth);
                emit Cancel(hash, remain, info.isSell);
            } else {
                emit Cancel(hash, 0, info.isSell);
            }
        }
    }

    function sell(bytes32 hash, uint amount) public {
        OrderInfo storage info = orderInfos[hash];
        bool find = false;
        if (info.limitUser.length > 0) {
            for (uint i = 0; i < info.limitUser.length; i++) {
                if (info.limitUser[i] == msg.sender) {
                    find = true;
                    break;
                }
            }
            require(find);
        }

        require(info.fill < info.eth);
        require(info.expires >= now);

        uint remain = info.eth - info.fill;

        uint remainAmount = remain.mul(info.amount).div(info.eth);

        uint tradeAmount = remainAmount < amount ? remainAmount : amount;

        ERC20(info.token).safeTransferFrom(msg.sender, this, tradeAmount);

        uint total = info.eth.mul(tradeAmount).div(info.amount);

        msg.sender.transfer(total);

        if (info.isSpecialERC20) {
            SpecialERC20(info.token).transfer(info.owner, tradeAmount);
        } else {
            ERC20(info.token).transfer(info.owner, tradeAmount);
        }

        info.fill = info.fill.add(total);

        emit Trade(
            hash,
            msg.sender,
            info.token,
            tradeAmount,
            info.owner,
            total
        );
    }

    function purchase(bytes32 hash, uint amount) public payable {
        OrderInfo storage info = orderInfos[hash];
        bool find = false;
        if (info.limitUser.length > 0) {
            for (uint i = 0; i < info.limitUser.length; i++) {
                if (info.limitUser[i] == msg.sender) {
                    find = true;
                    break;
                }
            }
            require(find);
        }

        require(info.fill < info.amount);
        require(info.expires >= now);

        uint remainAmount = info.amount - info.fill;

        uint tradeAmount = remainAmount < amount ? remainAmount : amount;

        uint total = info.eth.mul(tradeAmount).div(info.amount);

        require(msg.value >= total);
        if (msg.value > total) {

            msg.sender.transfer(msg.value - total);
        }

        info.owner.transfer(total);
        if (info.isSpecialERC20) {
            SpecialERC20(info.token).transfer(msg.sender, tradeAmount);
        } else {
            ERC20(info.token).transfer(msg.sender, tradeAmount);
        }
        info.fill = info.fill.add(tradeAmount);

        emit Trade(
            hash,
            info.owner,
            info.token,
            tradeAmount,
            msg.sender,
            total
        );
    }
}
