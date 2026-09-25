"""
Ermittelt den aktuellen USD-Preis eines Tokens über die
kostenlose CoinGecko-API (kein API-Key noetig, aber Rate-Limits
beachten: ca. 10-30 Anfragen/Minute im Free-Tier).
"""

import time
import requests

# Mapping von unserer chain-Bezeichnung auf CoinGecko-Plattform-IDs
CHAIN_TO_PLATFORM = {
    "ethereum": "ethereum",
    "bsc": "binance-smart-chain",
    "solana": "solana",
}

_price_cache = {}  # token_address -> (price, timestamp)
CACHE_TTL_SECONDS = 60


def get_token_price_usd(token_address: str, chain: str) -> float:
    """Gibt den aktuellen USD-Preis fuer einen Token zurueck (0.0 bei Fehler/unbekannt)."""
    if not token_address:
        return 0.0

    cache_key = f"{chain}:{token_address.lower()}"
    cached = _price_cache.get(cache_key)
    if cached and (time.time() - cached[1]) < CACHE_TTL_SECONDS:
        return cached[0]

    platform = CHAIN_TO_PLATFORM.get(chain)
    if not platform:
        return 0.0

    url = f"https://api.coingecko.com/api/v3/simple/token_price/{platform}"
    params = {
        "contract_addresses": token_address,
        "vs_currencies": "usd",
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        price = data.get(token_address.lower(), {}).get("usd", 0.0)
        _price_cache[cache_key] = (price, time.time())
        return price
    except Exception:
        return 0.0


def get_usd_value(amount_raw: str, decimals: int, token_address: str, chain: str) -> float:
    """Rechnet einen rohen Token-Betrag (wie von Etherscan geliefert) in USD um."""
    try:
        amount = int(amount_raw) / (10 ** decimals)
    except (ValueError, TypeError):
        return 0.0
    price = get_token_price_usd(token_address, chain)
    return amount * price
