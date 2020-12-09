from __future__ import annotations
from typing import List, Dict, Optional
from sqlalchemy import create_engine
from datetime import datetime

DB_PATH = "/database/accounts.db"
db_connect = create_engine(f'sqlite://{DB_PATH}')


def get_acc(id: str) -> dict:
    """
    A function to get an account with Account# = <id> from the database.
    Returns a Dictionary
    """
    conn = db_connect.connect()
    query = conn.execute(f"""select * from ACCOUNTS where "Account#" = {id}""")
    result = dict(*[zip(tuple(query.keys()), i) for i in query.cursor])

    return result


def get_transactions(id: str) -> List[dict]:
    """
    A function to get list of transactions with Account# = <id> from the database.
    Returns a List of Dictionaries
    """
    conn = db_connect.connect()
    query = conn.execute(f"""select * from TRANSACTIONS where "ToAcc" = "{id}" OR "FromAcc" = "{id}" """)
    result = [dict(zip(tuple(query.keys()), i)) for i in query.cursor]
    return result


def get_transaction(id: str) -> List[dict]:
    """
    A function to get Transaction with Transaction# = <id> from the database.
    Returns a Dictionary
    """
    conn = db_connect.connect()
    query = conn.execute(f"""select * from TRANSACTIONS where "Transaction#" = {id}""")
    result = dict(*[zip(tuple(query.keys()), i) for i in query.cursor])

    return result


def new_transaction(fr: str, to: str, amount: float, comments: str, date=datetime.now()) -> dict:
    """
    A function to put a Transaction into the database.
    Returns the dictionary for the Transaction.
    """
    date = date.strftime("%Y-%m-%d %H:%M:%S")
    conn = db_connect.connect()
    conn.execute(f"""INSERT INTO TRANSACTIONS ("ToAcc", "FromAcc", "Amount", "Comments" ,"DateTime")
    VALUES("{to}","{fr}",{amount},"{comments}","{date}");""")

    query = conn.execute(f"""SELECT last_insert_rowid();""")
    id = query.fetchone()[0]

    transaction = {
        "Transaction#": id,
        "FromAcc": fr,
        "ToAcc": to,
        "Amount": amount,
        "Comments": comments,
        "DateTime": date
    }

    return transaction
