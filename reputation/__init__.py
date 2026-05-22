# GitBlock Reputation System

import time
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class ReputationEntry:
    node_id: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_latency_ms: float = 0.0
    quality_scores: list[float] = field(default_factory=list)
    uptime_checks: list[bool] = field(default_factory=list)
    last_updated: float = 0.0


class ReputationEngine:
    """
    Reputation scoring engine for GitBlock nodes.

    Score (0.0-1.0) based on:
    - Success rate (40%)
    - Average latency (20%)
    - Response quality from verification (30%)
    - Uptime consistency (10%)
    """

    def __init__(self):
        self.entries: dict[str, ReputationEntry] = defaultdict(lambda: ReputationEntry(node_id=""))

    def record_request(self, node_id: str, success: bool, latency_ms: float = 0.0):
        entry = self.entries[node_id]
        entry.node_id = node_id
        entry.total_requests += 1
        if success:
            entry.successful_requests += 1
        else:
            entry.failed_requests += 1
        entry.total_latency_ms += latency_ms
        entry.last_updated = time.time()

    def record_quality(self, node_id: str, score: float):
        entry = self.entries[node_id]
        entry.quality_scores.append(max(0.0, min(1.0, score)))
        if len(entry.quality_scores) > 100:
            entry.quality_scores = entry.quality_scores[-100:]

    def record_uptime(self, node_id: str, is_up: bool):
        entry = self.entries[node_id]
        entry.uptime_checks.append(is_up)
        if len(entry.uptime_checks) > 1000:
            entry.uptime_checks = entry.uptime_checks[-1000:]

    def get_score(self, node_id: str) -> float:
        entry = self.entries.get(node_id)
        if not entry or entry.total_requests == 0:
            return 0.5
        success_rate = entry.successful_requests / entry.total_requests
        if entry.total_requests > 0:
            avg_latency = entry.total_latency_ms / entry.total_requests
            latency_score = max(0, 1.0 - (avg_latency / 2000))
        else:
            latency_score = 0.5
        quality_score = (sum(entry.quality_scores) / len(entry.quality_scores)) if entry.quality_scores else 0.5
        uptime_score = (sum(entry.uptime_checks) / len(entry.uptime_checks)) if entry.uptime_checks else 0.5
        score = success_rate * 0.40 + latency_score * 0.20 + quality_score * 0.30 + uptime_score * 0.10
        return round(min(1.0, max(0.0, score)), 4)

    def get_all_scores(self) -> dict[str, float]:
        return {nid: self.get_score(nid) for nid in self.entries}

    def get_details(self, node_id: str) -> dict:
        entry = self.entries.get(node_id)
        if not entry:
            return {"node_id": node_id, "score": 0.5, "no_data": True}
        return {
            "node_id": node_id,
            "score": self.get_score(node_id),
            "total_requests": entry.total_requests,
            "success_rate": (entry.successful_requests / entry.total_requests) if entry.total_requests > 0 else 0,
            "avg_latency_ms": (entry.total_latency_ms / entry.total_requests) if entry.total_requests > 0 else 0,
            "quality_avg": (sum(entry.quality_scores) / len(entry.quality_scores)) if entry.quality_scores else None,
            "uptime_rate": (sum(entry.uptime_checks) / len(entry.uptime_checks)) if entry.uptime_checks else None,
        }
