"""
Fragt Buy-Transaktionen der beobachteten Wallets ab.

Diese Datei ist bewusst als austauschbares Grundgeruest gehalten:
je nach Chain (Ethereum, BSC, Solana) brauchst du einen anderen
Datenanbieter. Etherscan/BscScan/Solscan bieten kostenlose Free-Tier
APIs mit Rate-Limits, fuer produktiven Einsatz lohnt sich ein
dedizierter Anbieter wie Alchemy, QuickNode oder Nansen.
"""

import os
import requests


class OnchainClient:
    def __init__(self, chain: str):
        self.chain = chain
        self.api_key = os.getenv(f"{chain.upper()}SCAN_API_KEY", "")
        self.base_url = {
            "ethereum": "https://api.etherscan.io/api",
            "bsc": "https://api.bscscan.com/api",
        }.get(chain)

    def get_recent_token_transfers(self, wallet_address: str, limit: int = 20):
        """
        Holt die letzten Token-Transfers (Kaeufe) einer Wallet.
        Gibt eine Liste von dicts zurueck: token, amount, usd_value, timestamp, tx_hash
        """
        if not self.base_url:
            raise NotImplementedError(
                f"Chain '{self.chain}' noch nicht implementiert. "
                "Fuer Solana z.B. Solscan-API oder Helius nutzen."
            )

        params = {
            "module": "account",
            "action": "tokentx",
            "address": wallet_address,
            "sort": "desc",
            "apikey": self.api_key,
        }
        response = requests.get(self.base_url, params=params, timeout=10)
        response.raise_for_status()
        result = response.json().get("result", [])

        transfers = []
        for tx in result[:limit]:
            # Nur eingehende Transfers = Kaeufe der beobachteten Wallet
            if tx.get("to", "").lower() != wallet_address.lower():
                continue
            transfers.append({
                "token": tx.get("tokenSymbol"),
                "token_address": tx.get("contractAddress"),
                "amount": tx.get("value"),
                "decimals": int(tx.get("tokenDecimal", 18) or 18),
                "timestamp": tx.get("timeStamp"),
                "tx_hash": tx.get("hash"),
            })
        return transfers
