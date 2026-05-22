# GitBlock Verification — Spot-check inference quality

import random
import time
from dataclasses import dataclass


@dataclass
class VerificationResult:
    node_id: str
    request_id: str
    passed: bool
    quality_score: float  # 0.0-1.0
    method: str  # "consensus", "spot_check", "hash_match"
    details: str = ""
    timestamp: float = 0.0

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = time.time()


class VerificationEngine:
    """
    Verification layer for GitBlock inference quality.

    Methods:
    1. Consensus: Same prompt sent to 3+ nodes, responses compared
    2. Spot check: Random requests duplicated to trusted validator
    3. Hash match: Deterministic prompts checked against known-good hashes
    """

    SPOT_CHECK_RATE = 0.01
    CONSENSUS_THRESHOLD = 0.7

    def __init__(self):
        self.results: list[VerificationResult] = []
        self.spot_check_queue: list[dict] = []

    def should_spot_check(self) -> bool:
        return random.random() < self.SPOT_CHECK_RATE

    def verify_consensus(self, node_id: str, request_id: str, responses: list[str]) -> VerificationResult:
        if len(responses) < 2:
            return VerificationResult(node_id=node_id, request_id=request_id, passed=True, quality_score=0.5, method="consensus", details="Not enough responses for consensus")
        similarities = []
        for i in range(len(responses)):
            for j in range(i + 1, len(responses)):
                similarities.append(self._simple_similarity(responses[i], responses[j]))
        avg_similarity = sum(similarities) / len(similarities)
        passed = avg_similarity >= self.CONSENSUS_THRESHOLD
        return VerificationResult(node_id=node_id, request_id=request_id, passed=passed, quality_score=avg_similarity, method="consensus", details=f"Pairwise similarity: {avg_similarity:.3f} (threshold: {self.CONSENSUS_THRESHOLD})")

    def verify_spot_check(self, node_id: str, request_id: str, node_response: str, validator_response: str) -> VerificationResult:
        similarity = self._simple_similarity(node_response, validator_response)
        passed = similarity >= 0.6
        return VerificationResult(node_id=node_id, request_id=request_id, passed=passed, quality_score=similarity, method="spot_check", details=f"Validator similarity: {similarity:.3f}")

    def record_result(self, result: VerificationResult):
        self.results.append(result)
        if len(self.results) > 10000:
            self.results = self.results[-10000:]

    def get_node_stats(self, node_id: str) -> dict:
        node_results = [r for r in self.results if r.node_id == node_id]
        if not node_results:
            return {"node_id": node_id, "total_checks": 0}
        passed = sum(1 for r in node_results if r.passed)
        return {
            "node_id": node_id,
            "total_checks": len(node_results),
            "passed": passed,
            "pass_rate": round(passed / len(node_results), 3),
            "avg_quality": round(sum(r.quality_score for r in node_results) / len(node_results), 3),
        }

    @staticmethod
    def _simple_similarity(a: str, b: str) -> float:
        if not a or not b:
            return 0.0
        def trigrams(s: str) -> set[str]:
            return {s[i:i+3] for i in range(max(0, len(s) - 2))}
        a_tri, b_tri = trigrams(a.lower()), trigrams(b.lower())
        if not a_tri or not b_tri:
            return 0.0
        return len(a_tri & b_tri) / len(a_tri | b_tri)
