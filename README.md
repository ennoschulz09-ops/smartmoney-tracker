# SmartMoney Tracker

Ein Onchain-Analyse-Tool, das die Kaufaktivität von "Smart Money"-Wallets
(historisch erfolgreiche/frühe Investoren) beobachtet und daraus
Kauf-Signale für Coins ableitet.

**Prinzip:** Je mehr unterschiedliche Smart-Money-Wallets einen Coin kaufen
und je mehr Kapital dabei investiert wird, desto stärker das Signal.

---

## Projektstruktur

```
smartmoney-tracker/
├── README.md                  # Diese Datei (Projekt-Index)
├── requirements.txt           # Python-Abhängigkeiten
├── .env.example                # Vorlage für API-Keys / Secrets
├── .gitignore
├── config/
│   ├── wallets.yaml            # Liste der beobachteten Smart-Money-Wallets
│   └── settings.yaml           # Schwellenwerte, Gewichtungen, Intervalle
├── src/
│   ├── __init__.py
│   ├── main.py                  # Einstiegspunkt: startet den Tracking-Loop
│   ├── onchain_client.py        # Abfrage von Onchain-Daten (Etherscan/Solscan/etc.)
│   ├── scoring.py               # Signal-Scoring-Logik
│   ├── storage.py               # Speicherung der erkannten Trades/Coins
│   └── notifier.py              # Telegram/Discord-Benachrichtigung
└── data/
    └── trades.db                 # lokale SQLite-DB (wird zur Laufzeit erstellt)
```

## Ablauf (High-Level)

1. `config/wallets.yaml` enthält die Liste der zu beobachtenden Wallets.
2. `onchain_client.py` fragt in regelmäßigen Abständen neue Buy-Transaktionen
   dieser Wallets ab.
3. `scoring.py` aggregiert pro Coin: Anzahl beteiligter Wallets + investiertes
   Kapital → berechnet einen Score.
4. Überschreitet der Score einen Schwellenwert (`settings.yaml`), sendet
   `notifier.py` einen Alert.

## Setup

```bash
git clone <dein-repo-url>
cd smartmoney-tracker
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # API-Keys eintragen
python src/main.py
```

## Nächste Schritte / TODO

- [ ] Wallet-Liste in `config/wallets.yaml` befüllen
- [ ] API-Key für gewählten Onchain-Datenanbieter eintragen (`.env`)
- [ ] Telegram-Bot-Token für Benachrichtigungen einrichten
- [ ] Scoring-Gewichtungen in `config/settings.yaml` anpassen
- [ ] Tests schreiben (`tests/`)

## Lizenz

MIT (oder nach Wunsch anpassen)
