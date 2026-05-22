# GitBlock Phase 3 — Architecture

## Overview

Phase 3 transforms GitBlock from a centralized API proxy into a decentralized network where anyone can contribute GPU compute and earn tokens.

## Components

### Node Server (`node/`)
Runs on operator's machine:
- Loads models onto GPU (via llama.cpp or PyTorch)
- Connects to GitBlock router via WebSocket
- Receives inference requests, returns responses
- Reports status (load, latency, GPU memory) via heartbeats

### Router (`router/`)
Central routing layer:
- Maintains registry of all active nodes
- Routes requests to best available node
- Scoring: reputation (40%) + load (30%) + latency (30%)
- Handles node discovery and health monitoring

### Reputation (`reputation/`)
Scores nodes (0.0-1.0) based on:
- Success rate (40% weight)
- Average latency (20% weight)
- Response quality from verification (30% weight)
- Uptime consistency (10% weight)

### Rewards (`rewards/`)
Distributes GitBlock Tokens (GBT):
- Base reward depends on model complexity (1-5 GBT per request)
- Quality multiplier: 0.5x to 2.0x
- Reputation multiplier: 0.5x to 1.5x
- Uptime bonus: 1.1x for consistent nodes
- Halving every 2 years

### Verification (`verification/`)
Ensures inference quality:
1. Consensus: Same prompt to 3+ nodes, responses compared
2. Spot check: 1% of requests duplicated to validator nodes
3. Hash match: Deterministic prompts checked against known-good outputs

### SDK (`sdk/`)
Python SDK for node operators:
```python
from sdk import GitBlockNode
node = GitBlockNode(wallet="0x...")
node.register(models=["mistral-7b"])
balance = node.get_balance()
```

### Smart Contracts (`contracts/`)
Solidity interfaces (not deployed):
- `GitBlockToken.sol` — ERC-20 GBT token
- `NodeRegistry.sol` — On-chain node registry

## Tokenomics

| Allocation | Percentage | Amount |
|-----------|-----------|--------|
| Node Rewards Pool | 40% | 400,000,000 GBT |
| Community Treasury | 30% | 300,000,000 GBT |
| Team & Development | 20% | 200,000,000 GBT |
| Early Adopters Airdrop | 10% | 100,000,000 GBT |

## Activation Criteria

Phase 3 activates when:
1. User base exceeds 1,000 active users
2. Node software is stable and tested
3. Tokenomics model is finalized
4. Smart contracts are audited
