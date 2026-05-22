# GitBlock Rewards Engine — Token distribution

import time
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class RewardEvent:
    node_id: str
    wallet_address: str
    amount_gbt: float
    request_id: str
    model: str
    quality_multiplier: float = 1.0
    reputation_multiplier: float = 1.0
    timestamp: float = 0.0

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = time.time()


class RewardsEngine:
    """
    GitBlock Token (GBT) rewards distribution engine.

    Tokenomics:
    - Total Supply: 1,000,000,000 GBT
    - Node Rewards Pool: 400,000,000 GBT
    - Halving every 2 years

    Rewards per request:
    base_reward * halving_factor * quality_mult * reputation_mult * uptime_mult
    """

    BASE_REWARDS = {
        "mistral-7b": 1.0, "gemma-4-9b": 1.0,
        "phi-3-14b": 2.0,
        "codellama-34b": 3.0, "yi-1.5-34b": 3.0, "deepseek-coder-33b": 3.0,
        "llama-3.3-70b": 5.0, "qwen-2.5-72b": 5.0,
    }
    TOTAL_SUPPLY = 1_000_000_000
    REWARDS_POOL = 400_000_000
    HALVING_INTERVAL_SECONDS = 2 * 365.25 * 24 * 3600

    def __init__(self):
        self.distribution_history: list[RewardEvent] = []
        self.pending_balances: dict[str, float] = defaultdict(float)
        self.total_distributed: float = 0.0
        self.epoch_start: float = time.time()

    def calculate_reward(self, node_id: str, wallet_address: str, model: str,
                         quality: float = 1.0, reputation: float = 0.5,
                         uptime_bonus: bool = False) -> RewardEvent:
        base = self.BASE_REWARDS.get(model, 1.0)
        epochs_elapsed = (time.time() - self.epoch_start) / self.HALVING_INTERVAL_SECONDS
        halving_factor = 0.5 ** int(epochs_elapsed)
        quality_mult = 0.5 + (quality * 1.5)
        rep_mult = 0.5 + (reputation * 1.0)
        uptime_mult = 1.1 if uptime_bonus else 1.0
        amount = base * halving_factor * quality_mult * rep_mult * uptime_mult
        return RewardEvent(
            node_id=node_id, wallet_address=wallet_address,
            amount_gbt=round(amount, 4), request_id="", model=model,
            quality_multiplier=round(quality_mult, 3),
            reputation_multiplier=round(rep_mult, 3),
        )

    def distribute(self, reward: RewardEvent):
        if self.total_distributed + reward.amount_gbt > self.REWARDS_POOL:
            remaining = self.REWARDS_POOL - self.total_distributed
            if remaining <= 0:
                return
            reward.amount_gbt = remaining
        self.pending_balances[reward.wallet_address] += reward.amount_gbt
        self.total_distributed += reward.amount_gbt
        self.distribution_history.append(reward)

    def get_balance(self, wallet_address: str) -> float:
        return self.pending_balances.get(wallet_address, 0.0)

    def get_stats(self) -> dict:
        return {
            "total_distributed_gbt": round(self.total_distributed, 4),
            "remaining_pool_gbt": round(self.REWARDS_POOL - self.total_distributed, 4),
            "pool_utilization_pct": round((self.total_distributed / self.REWARDS_POOL) * 100, 2),
            "total_events": len(self.distribution_history),
            "unique_operators": len(self.pending_balances),
            "halving_epochs_elapsed": int((time.time() - self.epoch_start) / self.HALVING_INTERVAL_SECONDS),
        }
