// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title NodeRegistry
 * @dev On-chain registry for GitBlock nodes
 * @notice Phase 3 — interface definition only
 */
interface INodeRegistry {
    struct Node {
        address operator;
        string[] models;
        uint256 reputationScore;
        uint256 totalRequests;
        uint256 registeredAt;
        bool isActive;
    }

    function registerNode(string[] calldata models) external;
    function deactivateNode(uint256 nodeId) external;
    function updateReputation(uint256 nodeId, uint256 newScore) external;
    function getNode(uint256 nodeId) external view returns (Node memory);
    function getOperatorNodes(address operator) external view returns (uint256[] memory);
    function getActiveNodeCount() external view returns (uint256);
}
