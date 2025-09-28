from atm_service import BankAPI, CashBin, CardReader
from functools import wraps


def authenticate(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.session.get("authenticated"):
            raise PermissionError("Not authenticated")
        return func(self, *args, **kwargs)
    return wrapper


class ATMController:
    def __init__(self, bank_api: BankAPI, card_reader: CardReader, cash_bin: CashBin):
        self.bank_api = bank_api
        self.card_reader = card_reader
        self.cash_bin = cash_bin
        self.session = {}

    def insert_card(self, account_id: str):
        card = self.card_reader.insert(account_id)
        self.session = {"account_id": card["account_id"], "authenticated": False}

    def eject_card(self):
        self.card_reader.eject()
        self.session = {}

    def enter_pin(self, pin: str) -> bool:
        account_id = self.session.get("account_id")
        if not account_id:
            return False

        is_validated = self.bank_api.validate_pin(account_id, pin)

        if is_validated:
            self.session["authenticated"] = True
            return True

        return False

    @authenticate
    def check_balance(self):
        return self.bank_api.get_balance(self.session["account_id"])

    @authenticate
    def deposit(self, amount: int) -> bool:
        is_cash_bin_deposited = self.cash_bin.deposit(amount)

        if not is_cash_bin_deposited:
            return False

        return self.bank_api.deposit(self.session["account_id"], amount)

    @authenticate
    def withdraw(self, amount: int):
        is_withdrawn_from_bank = self.bank_api.withdraw(self.session["account_id"], amount)

        if not is_withdrawn_from_bank:
            return False

        is_withdrawn_from_cash_bin = self.cash_bin.withdraw(amount)

        if not is_withdrawn_from_cash_bin:
            self.bank_api.deposit(self.session["account_id"], amount)
            return False

        return True
