# GitBlock Phase 3 — Tests
# Run with: pytest tests/ -v

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from node import NodeServer, NodeConfig
from router import Router
from reputation import ReputationEngine
from rewards import RewardsEngine
from verification import VerificationEngine


class TestNode:
    def test_node_creation(self):
        config = NodeConfig(models=["mistral-7b"])
        server = NodeServer(config)
        assert server.config.models == ["mistral-7b"]
        assert server.config.node_id != ""

    def test_placeholder_inference(self):
        config = NodeConfig(models=["mistral-7b"])
        server = NodeServer(config)
        response = server._placeholder_inference("mistral-7b", [{"role": "user", "content": "hi"}], 100)
        assert "GitBlock Node" in response


class TestRouter:
    def test_register_and_route(self):
        router = Router()
        router.register_node("node-1", ["mistral-7b", "llama-3.3-70b"])
        router.update_node_status("node-1", {"current_load": 0, "avg_latency_ms": 100})
        decision = router.route("mistral-7b")
        assert decision is not None
        assert decision.node_id == "node-1"

    def test_no_matching_node(self):
        router = Router()
        router.register_node("node-1", ["mistral-7b"])
        router.update_node_status("node-1", {"current_load": 0, "avg_latency_ms": 100})
        decision = router.route("llama-3.3-70b")
        assert decision is None

    def test_full_node_skipped(self):
        router = Router()
        router.register_node("node-1", ["mistral-7b"])
        router.update_node_status("node-1", {"current_load": 4, "avg_latency_ms": 100})
        decision = router.route("mistral-7b")
        assert decision is None

    def test_prefers_less_loaded(self):
        router = Router()
        router.register_node("node-1", ["mistral-7b"])
        router.register_node("node-2", ["mistral-7b"])
        router.update_node_status("node-1", {"current_load": 3, "avg_latency_ms": 100})
        router.update_node_status("node-2", {"current_load": 0, "avg_latency_ms": 100})
        results = [router.route("mistral-7b").node_id for _ in range(100)]
        assert results.count("node-2") > results.count("node-1")

    def test_available_models(self):
        router = Router()
        router.register_node("node-1", ["mistral-7b", "llama-3.3-70b"])
        router.register_node("node-2", ["mistral-7b", "qwen-2.5-72b"])
        models = router.get_available_models()
        assert set(models) == {"mistral-7b", "llama-3.3-70b", "qwen-2.5-72b"}


class TestReputation:
    def test_neutral_score(self):
        engine = ReputationEngine()
        assert engine.get_score("unknown") == 0.5

    def test_high_success_rate(self):
        engine = ReputationEngine()
        for _ in range(100):
            engine.record_request("node-1", success=True, latency_ms=50)
        score = engine.get_score("node-1")
        assert score > 0.7

    def test_low_success_rate(self):
        engine = ReputationEngine()
        for _ in range(100):
            engine.record_request("node-1", success=False, latency_ms=5000)
        score = engine.get_score("node-1")
        assert score < 0.3


class TestRewards:
    def test_base_reward(self):
        engine = RewardsEngine()
        reward = engine.calculate_reward("node-1", "0xabc", "mistral-7b")
        assert reward.amount_gbt > 0

    def test_larger_model_more_reward(self):
        engine = RewardsEngine()
        small = engine.calculate_reward("node-1", "0xabc", "mistral-7b")
        large = engine.calculate_reward("node-1", "0xabc", "llama-3.3-70b")
        assert large.amount_gbt > small.amount_gbt

    def test_quality_multiplier(self):
        engine = RewardsEngine()
        low_q = engine.calculate_reward("node-1", "0xabc", "mistral-7b", quality=0.0)
        high_q = engine.calculate_reward("node-1", "0xabc", "mistral-7b", quality=1.0)
        assert high_q.amount_gbt > low_q.amount_gbt

    def test_distribution(self):
        engine = RewardsEngine()
        reward = engine.calculate_reward("node-1", "0xabc", "llama-3.3-70b", quality=0.9, reputation=0.8)
        engine.distribute(reward)
        assert engine.get_balance("0xabc") > 0

    def test_pool_exhaustion(self):
        engine = RewardsEngine()
        engine.total_distributed = engine.REWARDS_POOL - 0.05
        reward = engine.calculate_reward("node-1", "0xabc", "llama-3.3-70b")
        engine.distribute(reward)
        assert engine.total_distributed <= engine.REWARDS_POOL


class TestVerification:
    def test_consensus_pass(self):
        engine = VerificationEngine()
        responses = ["The capital of France is Paris.", "France's capital is Paris.", "Paris is the capital of France."]
        result = engine.verify_consensus("node-1", "req-1", responses)
        assert result.quality_score > 0

    def test_consensus_fail(self):
        engine = VerificationEngine()
        responses = ["The capital of France is Paris.", "42 is the answer to everything.", "Quantum physics is weird."]
        result = engine.verify_consensus("node-1", "req-1", responses)
        assert result.quality_score < 0.7

    def test_spot_check_rate(self):
        engine = VerificationEngine()
        checks = sum(1 for _ in range(10000) if engine.should_spot_check())
        assert 50 < checks < 200


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
