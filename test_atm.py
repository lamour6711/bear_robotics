import pytest
import threading

from atm_controller import ATMController
from atm_service import BankAPI, CardReader, CashBin


def setup_atm():
    bank = BankAPI({
        "12345": {"pin": "1111", "balance": 1000},
        "67890": {"pin": "2222", "balance": 500},
    })
    cash_bin = CashBin(cash=1000)
    card_reader_1 = CardReader()
    card_reader_2 = CardReader()
    atm1 = ATMController(bank, card_reader_1, cash_bin)
    atm2 = ATMController(bank, card_reader_2, cash_bin)
    return atm1, atm2, bank, cash_bin


def withdraw(atm, account_id, pin, amount, results, idx):
    atm.insert_card(account_id)
    if atm.enter_pin(pin):
        success = atm.withdraw(amount)
        results[idx] = success


def deposit(atm, account_id, pin, amount, results, idx):
    atm.insert_card(account_id)
    if atm.enter_pin(pin):
        success = atm.deposit(amount)
        results[idx] = success


def test_invalid_pin():
    atm, _, bank, _ = setup_atm()
    account_id = "12345"
    wrong_pin = "invalid password"

    atm.insert_card(account_id)
    authenticated = atm.enter_pin(wrong_pin)

    assert not authenticated

    with pytest.raises(PermissionError):
        atm.withdraw(100)

    assert bank.get_balance(account_id) == 1000


def test_over_withdrawal():
    atm, _, bank, _ = setup_atm()
    account_id = "67890"
    pin = "2222"
    atm.insert_card(account_id)
    assert atm.enter_pin(pin)

    success = atm.withdraw(100000)
    assert not success
    assert bank.get_balance(account_id) == 500


def test_over_cash_bin_withdrawal():
    atm, _, bank, cash_bin = setup_atm()
    account_id = "12345"
    pin = "1111"

    cash_bin.cash = 100
    atm.insert_card(account_id)
    assert atm.enter_pin(pin)
    success = atm.withdraw(200)

    assert not success
    assert bank.get_balance(account_id) == 1000


def test_concurrent_withdrawals():
    atm1, atm2, bank, cash_bin = setup_atm()
    account_id = "12345"
    pin = "1111"

    assert bank.get_balance(account_id) == 1000

    results = {}
    t1 = threading.Thread(target=withdraw, args=(atm1, account_id, pin, 700, results, 1))
    t2 = threading.Thread(target=withdraw, args=(atm2, account_id, pin, 700, results, 2))

    t1.start()
    t2.start()
    t1.join()
    t2.join()

    assert list(results.values()).count(True) == 1
    assert list(results.values()).count(False) == 1

    # Only one successful withdrawal should have been made
    assert bank.get_balance(account_id) == 300
    assert cash_bin.cash == 300


def test_concurrent_deposits():
    atm1, atm2, bank, cash_bin = setup_atm()

    account_id = "67890"
    pin = "2222"

    assert bank.get_balance(account_id) == 500

    results = {}
    t1 = threading.Thread(target=deposit, args=(atm1, account_id, pin, 200, results, 1))
    t2 = threading.Thread(target=deposit, args=(atm2, account_id, pin, 300, results, 2))

    t1.start()
    t2.start()
    t1.join()
    t2.join()

    # Assert both deposits
    assert all(results.values())
    assert bank.get_balance(account_id) == 1000
    assert cash_bin.cash == 1500

