"""
Einstiegspunkt: laedt Config, pollt Wallets in einer Schleife,
aggregiert Trades und verschickt Alerts bei starken Signalen.
"""

import time
import yaml
from pathlib import Path
from dotenv import load_dotenv

from onchain_client import OnchainClient
from scoring import aggregate_trades, find_signals
from storage import init_db, trade_exists, save_trade
from notifier import send_telegram_alert
from pricing import get_usd_value

BASE_DIR = Path(__file__).resolve().parent.parent


def load_yaml(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)


def main():
    load_dotenv()
    init_db()

    wallets_cfg = load_yaml(BASE_DIR / "config" / "wallets.yaml")["wallets"]
    settings = load_yaml(BASE_DIR / "config" / "settings.yaml")

    clients = {}

    print(f"Starte Tracking fuer {len(wallets_cfg)} Wallets...")

    while True:
        new_trades = []

        for wallet in wallets_cfg:
            chain = wallet["chain"]
            if chain not in clients:
                clients[chain] = OnchainClient(chain)

            try:
                transfers = clients[chain].get_recent_token_transfers(wallet["address"])
            except NotImplementedError as e:
                print(f"[Warnung] {e}")
                continue
            except Exception as e:
                print(f"[Fehler] Wallet {wallet['label']}: {e}")
                continue

            for t in transfers:
                if trade_exists(t["tx_hash"]):
                    continue
                usd_value = get_usd_value(
                    t["amount"], t["decimals"], t["token_address"], chain
                )
                save_trade(wallet["label"], t["token"], usd_value,
                           t["tx_hash"], t["timestamp"])
                new_trades.append({
                    "wallet_label": wallet["label"],
                    "token": t["token"],
                    "usd_value": usd_value,
                })

        if new_trades:
            aggregates = aggregate_trades(new_trades)
            signals = find_signals(
                aggregates,
                settings["scoring"]["weight_per_wallet"],
                settings["scoring"]["weight_per_usd"],
                settings["scoring"]["signal_threshold"],
            )
            for signal in signals:
                send_telegram_alert(signal)

        time.sleep(settings["poll_interval_seconds"])


if __name__ == "__main__":
    main()
