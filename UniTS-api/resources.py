from __future__ import annotations
from flask import Flask, jsonify, request
from flask_restful import Resource, Api, reqparse
from query import *
from account import Account, Transaction

BANK_NAME = "UniTS"

class Accounts(Resource):
    """
    Api resource to GET Account details
    """
    def get(self, acc_num: str):
        acc = get_acc(acc_num)
        acc["Bank"] = BANK_NAME
        return acc, 200


class Transactions(Resource):
    """
    Api resource to GET Transactions for an Account
    """
    def get(self, acc_num: str):
        trans = get_transactions(acc_num)
        return trans, 200


class R_Transaction(Resource):
    """
    Api resource to GET and POST Transactions
    """
    def get(self, trans_num: str):
        trans = get_transaction(trans_num)
        return trans, 200

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("FromAcc")
        parser.add_argument("ToAcc")
        parser.add_argument("Amount")
        parser.add_argument("Comments")
        params = parser.parse_args()

        trans = new_transaction(params["FromAcc"], params["ToAcc"], params["Amount"], params["Comments"])
        return trans, 200
