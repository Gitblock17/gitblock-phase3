// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title GitBlockToken (GBT)
 * @dev ERC-20 token for GitBlock node operator rewards
 * @notice Phase 3 — not deployed yet, interface definition only
 */
interface IGitBlockToken {
    function totalSupply() external view returns (uint256);
    function balanceOf(address account) external view returns (uint256);
    function transfer(address to, uint256 amount) external returns (bool);
    function approve(address spender, uint256 amount) external returns (bool);
    function allowance(address owner, address spender) external view returns (uint256);
    function mintRewards(address to, uint256 amount) external;
    function getRewardsPoolRemaining() external view returns (uint256);
    function getNodeOperatorCount() external view returns (uint256);
}
