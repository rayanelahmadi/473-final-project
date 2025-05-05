// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract XRP is ERC20 {
    constructor(uint256 initialSupply) ERC20("Test XRP", "XRP") {
        _mint(msg.sender, initialSupply);
    }
}
