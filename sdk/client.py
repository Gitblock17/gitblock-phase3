# GitBlock Node SDK — Client for node operators

import httpx
from dataclasses import dataclass


@dataclass
class NodeOperatorConfig:
    wallet_address: str
    api_key: str = ""
    gateway_url: str = "https://router.gitblock.org"
    node_port: int = 7860


class GitBlockNode:
    """
    SDK client for GitBlock node operators.

    Usage:
        node = GitBlockNode(wallet="0x...")
        node.register(models=["mistral-7b", "llama-3.3-70b"])
        balance = node.get_balance()
    """

    def __init__(self, wallet: str, gateway_url: str = "https://router.gitblock.org"):
        self.wallet = wallet
        self.gateway_url = gateway_url
        self.client = httpx.Client(timeout=30)

    def register(self, models: list[str]) -> dict:
        resp = self.client.post(f"{self.gateway_url}/api/nodes/register", json={"wallet_address": self.wallet, "models": models})
        resp.raise_for_status()
        return resp.json()

    def get_balance(self) -> dict:
        resp = self.client.get(f"{self.gateway_url}/api/rewards/balance", params={"wallet": self.wallet})
        resp.raise_for_status()
        return resp.json()

    def get_stats(self) -> dict:
        resp = self.client.get(f"{self.gateway_url}/api/nodes/stats", params={"wallet": self.wallet})
        resp.raise_for_status()
        return resp.json()

    def get_network_status(self) -> dict:
        resp = self.client.get(f"{self.gateway_url}/api/status")
        resp.raise_for_status()
        return resp.json()

    def close(self):
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
