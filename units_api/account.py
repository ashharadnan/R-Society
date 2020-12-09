from __future__ import annotations
from typing import List, Dict, TextIO, Optional
from datetime import datetime
import json
from query import *


class Account:
    """
        A class to objectify UniTS bank accounts

        === Public Attributes ===
        id: The account number
        balance: The remaining account balance
        opening_bal: The opening balance for the account
        name: The account holder's name
        phone: The account holder's phone number
        email: The account holder's email

        === Private Attributes ===
        _transactions: The list of transactions stored in the account
        _dictionary: The dictionary representation of the account
    """
    id: int
    opening_bal: float
    balance: float
    name: str
    phone: str
    email: str
    bank: str
    _transactions: List[Transaction]
    _dictionary: dict

    def __init__(self, data: dict):
        """
        Initialize the account object, with account data given as <data>.
        """
        self.id = data["Account#"]
        self.opening_bal = data["OpeningBalance"]
        self.name = data["FullName"]
        self.phone = data["Phone"]
        self.email = data["Email"]
        self.bank = data["Bank"]
        self._dictionary = data
        self._transactions = []

    def update_transactions(self, transactions: List[dict]) -> None:
        """
        Generate a list of <_transactions> from json data.
        """
        for t in transactions:
            self._transactions.append(Transaction(t))
            self.update_balance()

    def update_balance(self) -> None:
        """
        Calculate <balance>.
        """
        bal = self.opening_bal
        for t in self._transactions:
            if t.fr == str(self.id):
                bal -= t.amount
            else:
                bal += t.amount
        self.balance = bal
        self._dictionary["Balance"] = bal

    def list_transactions(self) -> List[Transaction]:
        """
        Returns a list of all the transactions of this account
        """
        return self._transactions

    def as_dict(self) -> dict:
        """
        Returns the dictionary representation of the account
        """
        return self._dictionary

    def get_transaction(self, tran_num: str) -> Transaction:
        """
        Returns a specific transaction of this account
        """
        for t in self._transactions:
            if t.id == int(tran_num):
                return t


class Transaction:
    """
    A class to objectify each transaction

    === Public attributes ===
    id: The transaction number
    fr: The name of the benefactor
    to: The name of the beneficiary
    amount: The amount of the transaction

    === Private Attributes ===
    _comments: Comments of the Transaction
    _datetime: The time and date of the transaction
    _dictionary: The dictionary representation of the transaction
    """
    id: int
    to: str
    fr: str
    amount: float
    _comments: str
    _datetime: datetime
    _dictionary: dict

    def __init__(self, data):
        """
        Initialize the transaction object, with json data given.
        """
        self.id = data["Transaction#"]
        self.fr = data["FromAcc"]
        self.to = data["ToAcc"]
        self.amount = data["Amount"]
        self._comments = data["Comments"]
        self._datetime = data["DateTime"]
        self._dictionary = data

    def as_dict(self):
        """
        Returns the dictionary representation of the account
        """
        return self._dictionary
