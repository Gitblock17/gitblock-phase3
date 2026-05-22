# GitBlock Router — Smart request routing

import asyncio
import time
import random
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class NodeInfo:
    node_id: str
    models: list[str]
    current_load: int = 0
    max_load: int = 4
    avg_latency_ms: float = 0.0
    reputation_score: float = 1.0
    wallet_address: str = ""
    last_heartbeat: float = 0.0
    is_alive: bool = True


@dataclass
class RoutingDecision:
    node_id: str
    reason: str
    score: float


class Router:
    """
    GitBlock Request Router.

    Selects the best available node based on:
    - Model availability
    - Current load (prefer less loaded)
    - Reputation score (prefer higher)
    - Latency (prefer lower)
    """

    def __init__(self):
        self.nodes: dict[str, NodeInfo] = {}
        self._request_count = 0

    def register_node(self, node_id: str, models: list[str], wallet: str = ""):
        self.nodes[node_id] = NodeInfo(
            node_id=node_id, models=models, wallet_address=wallet, last_heartbeat=time.time()
        )
        print(f"[Router] Registered node {node_id} with models: {models}")

    def unregister_node(self, node_id: str):
        self.nodes.pop(node_id, None)
        print(f"[Router] Unregistered node {node_id}")

    def update_node_status(self, node_id: str, status: dict):
        if node_id not in self.nodes:
            return
        node = self.nodes[node_id]
        node.current_load = status.get("current_load", node.current_load)
        node.avg_latency_ms = status.get("avg_latency_ms", node.avg_latency_ms)
        node.last_heartbeat = time.time()
        node.is_alive = True

    def route(self, model: str) -> Optional[RoutingDecision]:
        """Select the best node for a given model."""
        self._request_count += 1
        self._cleanup_dead_nodes()
        candidates = [
            n for n in self.nodes.values()
            if model in n.models and n.is_alive and n.current_load < n.max_load
        ]
        if not candidates:
            return None
        scored = []
        for node in candidates:
            load_ratio = 1.0 - (node.current_load / node.max_load)
            latency_score = max(0, 1.0 - (node.avg_latency_ms / 1000))
            rep = node.reputation_score
            score = (rep * 0.4) + (load_ratio * 0.3) + (latency_score * 0.3)
            score += random.uniform(0, 0.01)
            scored.append((node, score))
        scored.sort(key=lambda x: x[1], reverse=True)
        best_node, best_score = scored[0]
        return RoutingDecision(
            node_id=best_node.node_id,
            reason=f"score={best_score:.3f} (rep={best_node.reputation_score:.2f}, load={best_node.current_load}/{best_node.max_load}, latency={best_node.avg_latency_ms:.0f}ms)",
            score=best_score,
        )

    def get_available_models(self) -> list[str]:
        models = set()
        for node in self.nodes.values():
            if node.is_alive:
                models.update(node.models)
        return sorted(models)

    def get_status(self) -> dict:
        alive = [n for n in self.nodes.values() if n.is_alive]
        return {
            "total_nodes": len(self.nodes),
            "alive_nodes": len(alive),
            "total_requests_routed": self._request_count,
            "available_models": self.get_available_models(),
            "nodes": {
                nid: {"models": n.models, "load": f"{n.current_load}/{n.max_load}", "latency_ms": round(n.avg_latency_ms, 2), "reputation": round(n.reputation_score, 3), "alive": n.is_alive}
                for nid, n in self.nodes.items()
            },
        }

    def _cleanup_dead_nodes(self, timeout: float = 30.0):
        now = time.time()
        for node in self.nodes.values():
            if now - node.last_heartbeat > timeout:
                node.is_alive = False
