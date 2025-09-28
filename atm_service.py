import threading


class BankAPI:
    def __init__(self, accounts: dict):
        self.accounts = accounts
        self._lock = threading.Lock()

    def validate_pin(self, account_id: str, pin: str):
        account = self.accounts.get(account_id)
        return account and account["pin"] == pin

    def get_balance(self, account_id: str):
        with self._lock:
            return self.accounts[account_id]["balance"]

    def deposit(self, account_id: str, amount: int):
        if amount <= 0:
            return False

        with self._lock:
            self.accounts[account_id]["balance"] += amount

        return True

    def withdraw(self, account_id: str, amount: int):
        if amount <= 0:
            return False

        with self._lock:
            if self.accounts[account_id]["balance"] >= amount:
                self.accounts[account_id]["balance"] -= amount
                return True

            return False


class CardReader:
    def __init__(self):
        self.card = {}

    def insert(self, account_id: str):
        self.card = {"account_id": account_id}
        return self.card

    def eject(self):
        card = self.card
        self.card = None
        return card


class CashBin:
    def __init__(self, cash: int):
        self.cash = cash
        self._lock = threading.Lock()

    def withdraw(self, amount: int):
        with self._lock:
            if self.cash >= amount:
                self.cash -= amount
                return True

            return False

    def deposit(self, amount: int):
        if amount <= 0:
            return False

        with self._lock:
            self.cash += amount

        return True
