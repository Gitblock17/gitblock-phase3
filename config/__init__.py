# GitBlock Phase 3 — Configuration

from dataclasses import dataclass, field


@dataclass
class NetworkConfig:
    router_host: str = "0.0.0.0"
    router_port: int = 8080
    router_gateway_url: str = "wss://router.gitblock.org/node"
    heartbeat_interval: int = 10
    node_timeout: int = 30
    global_rate_limit: int = 1000
    per_user_rate_limit: int = 20


@dataclass
class RewardsConfig:
    token_name: str = "GitBlock Token"
    token_symbol: str = "GBT"
    total_supply: int = 1_000_000_000
    rewards_pool: int = 400_000_000
    halving_years: float = 2.0
    min_reward_gbt: float = 0.01
    payout_threshold_gbt: float = 10.0


@dataclass
class VerificationConfig:
    spot_check_rate: float = 0.01
    consensus_threshold: float = 0.7
    consensus_nodes: int = 3
    min_similarity: float = 0.6


@dataclass
class ReputationConfig:
    weight_success_rate: float = 0.40
    weight_latency: float = 0.20
    weight_quality: float = 0.30
    weight_uptime: float = 0.10
    neutral_score: float = 0.5
    decay_rate: float = 0.99


MODELS = {
    "llama-3.3-70b": {"tier": 3, "params": "70B", "type": "General Purpose", "provider": "Meta", "base_reward": 5.0},
    "qwen-2.5-72b": {"tier": 3, "params": "72B", "type": "General Purpose", "provider": "Alibaba", "base_reward": 5.0},
    "deepseek-coder-33b": {"tier": 2, "params": "33B", "type": "Code Generation", "provider": "DeepSeek", "base_reward": 3.0},
    "codellama-34b": {"tier": 2, "params": "34B", "type": "Code Generation", "provider": "Meta", "base_reward": 3.0},
    "yi-1.5-34b": {"tier": 2, "params": "34B", "type": "General Purpose", "provider": "01.AI", "base_reward": 3.0},
    "phi-3-14b": {"tier": 2, "params": "14B", "type": "Compact/Efficient", "provider": "Microsoft", "base_reward": 2.0},
    "mistral-7b": {"tier": 1, "params": "7B", "type": "Fast Inference", "provider": "Mistral AI", "base_reward": 1.0},
    "gemma-4-9b": {"tier": 1, "params": "9B", "type": "General Purpose", "provider": "Google", "base_reward": 1.0},
}
