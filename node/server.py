# GitBlock Node Server
# Runs on operator's machine, serves local model inference

import asyncio
import time
import uuid
import json
import hashlib
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class NodeConfig:
    """Configuration for a GitBlock node."""
    node_id: str = ""
    gpu_device: str = "auto"
    models: list[str] = field(default_factory=lambda: ["mistral-7b"])
    max_concurrent: int = 4
    port: int = 7860
    gateway_url: str = "wss://router.gitblock.org/node"
    wallet_address: str = ""
    max_memory_gb: float = 16.0
    max_vram_gb: float = 8.0
    request_timeout: int = 60


@dataclass
class NodeStatus:
    """Runtime status of a node."""
    node_id: str
    uptime: float = 0.0
    requests_served: int = 0
    requests_failed: int = 0
    avg_latency_ms: float = 0.0
    current_load: int = 0
    max_load: int = 4
    models_loaded: list[str] = field(default_factory=list)
    gpu_memory_used_gb: float = 0.0
    gpu_memory_total_gb: float = 0.0


class NodeServer:
    """
    GitBlock Node Server.

    Connects to the GitBlock router via WebSocket, receives inference
    requests, runs them on local GPU, and returns results.

    Usage:
        config = NodeConfig(models=["mistral-7b", "llama-3.3-70b"])
        server = NodeServer(config)
        await server.start()
    """

    def __init__(self, config: NodeConfig):
        self.config = config
        if not config.node_id:
            config.node_id = self._generate_node_id()
        self.status = NodeStatus(node_id=config.node_id, max_load=config.max_concurrent)
        self._running = False
        self._latencies: list[float] = []
        self._loaded_models: dict[str, object] = {}

    def _generate_node_id(self) -> str:
        raw = f"{self.config.wallet_address}-{self.config.gpu_device}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    async def start(self):
        """Start the node server and connect to router."""
        self._running = True
        self._start_time = time.time()
        print(f"[Node {self.config.node_id}] Starting on port {self.config.port}")
        print(f"[Node {self.config.node_id}] Models: {self.config.models}")
        print(f"[Node {self.config.node_id}] Gateway: {self.config.gateway_url}")
        # TODO: Phase 3 — connect to gateway WebSocket
        # TODO: Phase 3 — load models onto GPU
        # TODO: Phase 3 — serve inference requests
        print(f"[Node {self.config.node_id}] Ready. Waiting for requests...")
        await self._event_loop()

    async def _event_loop(self):
        while self._running:
            self.status.uptime = time.time() - self._start_time
            await asyncio.sleep(1)

    async def handle_request(self, request: dict) -> dict:
        """Handle an inference request from the router."""
        start = time.time()
        self.status.current_load += 1
        request_id = str(uuid.uuid4())
        try:
            model = request.get("model", "mistral-7b")
            messages = request.get("messages", [])
            max_tokens = request.get("max_tokens", 512)
            temperature = request.get("temperature", 0.7)
            stream = request.get("stream", False)
            # TODO: Phase 3 — run actual inference on local GPU
            response = self._placeholder_inference(model, messages, max_tokens)
            latency_ms = (time.time() - start) * 1000
            self._latencies.append(latency_ms)
            self.status.avg_latency_ms = sum(self._latencies[-100:]) / len(self._latencies[-100:])
            self.status.requests_served += 1
            return {
                "id": f"chatcmpl-{request_id}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": model,
                "choices": [{"index": 0, "message": {"role": "assistant", "content": response}, "finish_reason": "stop"}],
                "usage": {
                    "prompt_tokens": sum(len(m.get("content", "")) // 4 for m in messages),
                    "completion_tokens": len(response) // 4,
                    "total_tokens": 0,
                },
                "node_id": self.config.node_id,
            }
        except Exception as e:
            self.status.requests_failed += 1
            return {"error": str(e), "node_id": self.config.node_id}
        finally:
            self.status.current_load -= 1

    def _placeholder_inference(self, model: str, messages: list, max_tokens: int) -> str:
        return (
            f"[GitBlock Node {self.config.node_id}] "
            f"This is a placeholder response from model '{model}'. "
            f"Phase 3 inference not yet implemented. "
            f"Received {len(messages)} messages, max_tokens={max_tokens}."
        )

    def get_status(self) -> dict:
        return {
            "node_id": self.status.node_id,
            "uptime": self.status.uptime,
            "requests_served": self.status.requests_served,
            "requests_failed": self.status.requests_failed,
            "avg_latency_ms": round(self.status.avg_latency_ms, 2),
            "current_load": self.status.current_load,
            "max_load": self.status.max_load,
            "models_loaded": self.config.models,
            "gpu_memory_used_gb": self.status.gpu_memory_used_gb,
            "gpu_memory_total_gb": self.status.gpu_memory_total_gb,
        }

    async def stop(self):
        self._running = False
        # TODO: Phase 3 — unload models, close WebSocket
        print(f"[Node {self.config.node_id}] Stopped. Served {self.status.requests_served} requests.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="GitBlock Node Server")
    parser.add_argument("--gpu", default="auto", help="GPU device (auto, cuda:0, cpu)")
    parser.add_argument("--models", default="mistral-7b", help="Comma-separated model names")
    parser.add_argument("--port", type=int, default=7860, help="Server port")
    parser.add_argument("--max-concurrent", type=int, default=4, help="Max concurrent requests")
    parser.add_argument("--wallet", default="", help="Wallet address for rewards")
    parser.add_argument("--gateway", default="wss://router.gitblock.org/node", help="Router gateway URL")
    args = parser.parse_args()
    config = NodeConfig(
        gpu_device=args.gpu,
        models=[m.strip() for m in args.models.split(",")],
        port=args.port,
        max_concurrent=args.max_concurrent,
        wallet_address=args.wallet,
        gateway_url=args.gateway,
    )
    server = NodeServer(config)
    asyncio.run(server.start())
