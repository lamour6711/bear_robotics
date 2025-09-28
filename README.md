# ATM Simulation

This project implements an ATM simulation:
- **Insert card, enter PIN, check balance, deposit, withdraw**
- **BankAPI** simplifies a bank system with locking for concurrency
- **CardReader** and **CashBin** stubs for hardware
- **ATMController** orchestrates the workflow

## Requirements
- Python 3.9+
- pip
- pytest 8.2.2

## Test Setup
```bash
git clone <repo-url>
cd bear_robotics
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pytest -v
