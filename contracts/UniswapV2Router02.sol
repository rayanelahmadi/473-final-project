// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IWETH {
    function deposit() external payable;
    function transfer(address to, uint value) external returns (bool);
}

interface IERC20 {
    function transferFrom(address src, address dst, uint amount) external returns (bool);
    function transfer(address dst, uint amount) external returns (bool);
    function approve(address spender, uint amount) external returns (bool);
}

contract UniswapV2Router02 {
    address public factory;
    address public WETH;
    address public XRP;

    constructor(address _factory, address _WETH, address _XRP) {
        factory = _factory;
        WETH = _WETH;
        XRP = _XRP;
    }

    function swapETHForExactTokens(
    uint amountOut,              // Desired XRP amount
    address[] calldata path,
    address to,
    uint deadline
    ) external payable returns (uint[] memory amounts) {
        require(block.timestamp <= deadline, "EXPIRED");
        require(path.length == 2, "Only simple swaps allowed");
        require(path[0] == WETH, "Must start with WETH");
        require(path[1] == XRP, "Must end with XRP");

        // Fixed mock rate: 1 ETH = 1000 XRP => 1 XRP = 0.001 ETH
        uint fakeRate = 1000;

        // Calculate how much ETH is required to buy amountOut XRP
        uint requiredETH = amountOut / fakeRate;

        require(msg.value >= requiredETH, "Not enough ETH sent");

        // Deposit and hold exact required ETH as WETH
        IWETH(WETH).deposit{value: requiredETH}();
        IWETH(WETH).transfer(address(this), requiredETH);

        // Refund any extra ETH
        if (msg.value > requiredETH) {
            payable(msg.sender).transfer(msg.value - requiredETH);
        }

        // Transfer XRP to recipient
        IERC20(XRP).transfer(to, amountOut);

        amounts = new uint[](2);
        amounts[0] = requiredETH;
        amounts[1] = amountOut;
    }


    function swapExactTokensForETH(
    uint amountIn,
    uint amountOutMin,
    address[] calldata path,
    address to,
    uint deadline
    ) external returns (uint[] memory amounts) {
        require(block.timestamp <= deadline, "EXPIRED");
        require(path.length == 2, "Only simple swaps allowed");
        require(path[0] == XRP, "Must start with XRP");
        require(path[1] == WETH, "Must end with WETH");

        // Transfer XRP from sender
        IERC20(XRP).transferFrom(msg.sender, address(this), amountIn);

        // Fake rate: 1000 XRP = 1 ETH → 1 XRP = 0.001 ETH
        uint ethAmount = amountIn / 1000;
        require(ethAmount >= amountOutMin, "Slippage too high");

        // Send ETH to user
        payable(to).transfer(ethAmount);

        amounts = new uint[](2);
        amounts[0] = amountIn;
        amounts[1] = ethAmount;
    }


    receive() external payable {}
}
