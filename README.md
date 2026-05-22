# GitBlock Phase 3 — Decentralized Node Network

> Users run GPU nodes, earn tokens. Everyone gets free AI inference.

## What is Phase 3?

GitBlock Phase 3 turns the centralized proxy (Phase 1) into a decentralized network where anyone can contribute their GPU compute and earn GitBlock Tokens (GBT) for serving inference requests. Users still pay nothing — node operators are rewarded from a token pool.

## Architecture

```
User Request
    │
    ▼
┌─────────────┐
│   Router     │  ← Selects best node based on load, reputation, model
│  (Gateway)   │
└──────┬──────┘
       │
       ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Node A     │    │  Node B     │    │  Node C     │
│  GPU: 4090  │    │  GPU: A100  │    │  GPU: 3090  │
│  Models: 3  │    │  Models: 5  │    │  Models: 2  │
└─────────────┘    └─────────────┘    └─────────────┘
       │
       ▼
┌─────────────┐
│ Verification │  ← Spot-check responses for quality
│   Layer      │
└─────────────┘
       │
       ▼
┌─────────────┐
│  Rewards     │  ← Distribute GBT tokens to node operators
│  Engine      │
└─────────────┘
```

## Components

| Component | Directory | Description |
|-----------|-----------|-------------|
| Node Server | `node/` | Runs on operator's machine, serves inference via local model |
| Router | `router/` | Load balancer + smart routing (model, latency, reputation) |
| Reputation | `reputation/` | Scores nodes by uptime, latency, response quality |
| Rewards | `rewards/` | Token distribution engine (GBT) |
| Verification | `verification/` | Spot-check inference quality via consensus |
| SDK | `sdk/` | Python SDK for node operators |
| Contracts | `contracts/` | Solidity interfaces for on-chain settlement |
| Config | `config/` | Shared configuration schemas |

## Quick Start (Node Operator)

```bash
pip install gitblock-node
gitblock-node start --gpu auto --models llama-3.3-70b,mistral-7b
```

## Status

Phase 3 is in **planning/prototype**. The current GitBlock API (Phase 1) runs as a centralized proxy. Phase 3 will be activated when:
- [ ] User base exceeds 1,000 active users
- [ ] Node software is stable and tested
- [ ] Tokenomics model is finalized
- [ ] Smart contracts are audited

## Tokenomics (Draft)

| Metric | Value |
|--------|-------|
| Token | GitBlock Token (GBT) |
| Total Supply | 1,000,000,000 GBT |
| Node Rewards Pool | 40% (400M GBT) |
| Community Treasury | 30% (300M GBT) |
| Team & Development | 20% (200M GBT) |
| Early Adopters Airdrop | 10% (100M GBT) |

## License

MIT — same as GitBlock core.
