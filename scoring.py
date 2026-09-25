"""
Berechnet ein Signal-Staerke pro Coin, basierend auf Anzahl
beteiligter Smart-Money-Wallets und investiertem Kapital.
"""

from collections import defaultdict


class CoinAggregate:
    def __init__(self, token: str):
        self.token = token
        self.wallets = set()
        self.total_usd = 0.0

    @property
    def wallet_count(self):
        return len(self.wallets)

    def score(self, weight_per_wallet: float, weight_per_usd: float) -> float:
        return (
            self.wallet_count * weight_per_wallet
            + self.total_usd * weight_per_usd
        )


def aggregate_trades(trades: list) -> dict:
    """
    trades: Liste von dicts mit mind. 'token', 'wallet_label', 'usd_value'
    Rueckgabe: dict token -> CoinAggregate
    """
    aggregates = defaultdict(lambda: None)
    for trade in trades:
        token = trade["token"]
        if aggregates[token] is None:
            aggregates[token] = CoinAggregate(token)
        agg = aggregates[token]
        agg.wallets.add(trade["wallet_label"])
        agg.total_usd += trade.get("usd_value", 0.0)
    return dict(aggregates)


def find_signals(aggregates: dict, weight_per_wallet: float,
                  weight_per_usd: float, threshold: float) -> list:
    """Gibt Coins zurueck, deren Score den Schwellenwert ueberschreitet, sortiert nach Score."""
    signals = []
    for agg in aggregates.values():
        s = agg.score(weight_per_wallet, weight_per_usd)
        if s >= threshold:
            signals.append({
                "token": agg.token,
                "wallet_count": agg.wallet_count,
                "total_usd": agg.total_usd,
                "score": s,
            })
    signals.sort(key=lambda x: x["score"], reverse=True)
    return signals
