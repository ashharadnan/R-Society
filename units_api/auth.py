from __future__ import annotations
import os
from typing import List, Dict, Optional, Tuple
from sqlalchemy import create_engine
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from dotenv import load_dotenv
from twilio.rest import Client
from smtplib import SMTP_SSL
import requests
from account import Account

# This dictionary contains the addresses and ports for the bank servers running the API
BANK_SERVERS = {"UniTS" : "localhost:5002"}

OTP_GEN_URL = 'https://api.generateotp.com/'
DB_PATH = "/database/logins.db"
db_connect = create_engine(f'sqlite://{DB_PATH}')
load_dotenv()
twi = Client()


def send_message(phone: str, email: str, subject: str, message: str) -> bool:
    fr = os.getenv("EMAIL")
    to = email

    try:
        server = SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(os.getenv("EMAIL"), os.getenv("PASS"))
        msg = "\r\n".join([
            "From: UniTS",
            f"To: {to}",
            f"Subject: {subject}",
            "",
            message])
        server.sendmail(fr, to, msg)
        server.close()
    except:
        pass

    messages = twi.messages.create(to=f"+92{phone[1:]}", from_=os.getenv(
        'TWILIO_NUMBER'), body=message)


def user_exists(user: str, phone: str, email: str) -> Tuple[bool, str]:
    """
    Checks if a user already exists in a database.
    Returns true and a message
    """
    conn = db_connect.connect()
    query = conn.execute(f"""select "username" from USERS where "username" = "{user}" """)
    existing_user = query.fetchone()
    if existing_user:
        return(True, "Username already taken")
    query = conn.execute(f"""select "email" from USERS where "email" = "{email}" """)
    existing_user = query.fetchone()
    if existing_user:
        return(True, "Account with the specified email exists")
    query = conn.execute(f"""select "phone#" from USERS where "phone#" = "{phone}" """)
    existing_user = query.fetchone()
    if existing_user:
        return(True, "Account with the specified phone number exists")
    return False, None


def register_user(user: str, pw: str, phone: str, email: str) -> bool:
    """
    A function that registers new users to the database.
    Returns True if the register was successful.
    """
    conn = db_connect.connect()
    pw_hash = generate_password_hash(pw)
    try:
        conn.execute(f""" INSERT INTO USERS ("username", "pw_hash", "phone#", "email")
                    VALUES("{user}","{pw_hash}","{phone}","{email}");""")
        return True
    except Exception as e:
        return False


class User(UserMixin):
    user = None
    accounts = []

    def __init__(self, user: str):
        conn = db_connect.connect()
        query = conn.execute(f"""select "username","phone#","email" from USERS where "username" = "{user}" """)
        existing_user = query.fetchone()
        if existing_user:
            self.user = existing_user[0]
            self.phone = existing_user[1]
            self.email = existing_user[2]
        else:
            self.user = None

    def check_pw(self, pw: str):
        conn = db_connect.connect()
        query = conn.execute(f"""select "pw_hash" from USERS where "username" = "{self.user}" """)
        pw_hash = query.fetchone()
        if pw_hash is not None:
            if check_password_hash(pw_hash[0], pw):
                return True
        else:
            return False

    def generate_otp(self):
        r = requests.post(f"{OTP_GEN_URL}/generate",
                          data={'initiator_id': self.phone})
        if r.status_code == 201:
            data = r.json()
            otp_code = str(data["code"])
            message = f"Your UniTS One-Time-Password is: {otp_code}"
            subject = "UniTS Verification Code"
            send_message(self.phone, self.email, subject, message)

    def check_otp(self, otp: str):
        r = requests.post(f"{OTP_GEN_URL}/validate/{otp}/{self.phone}")
        if r.status_code == 200:
            data = r.json()
            status = data["status"]
            message = data["message"]
            return status, message
        return None, None

    def get_id(self):
        return self.user

    def update_accounts(self):
        conn = db_connect.connect()
        query = conn.execute(f"""select "Account#","Bank" from ACCOUNTS where "username" = "{self.user}" """)

        self.accounts = []
        for acc_num, bank in query:
            ip = BANK_SERVERS[bank]
            req = requests.request("GET", f"https://{ip}/a/{acc_num}", verify=False)
            account = Account(req.json())
            trans = requests.request("GET", f"https://{ip}/ts/{acc_num}", verify=False)
            account.update_transactions(trans.json())
            self.accounts.append(account)

    def get_total_balance(self) -> float:
        t = 0
        for account in self.accounts:
            account.update_balance()
            t += account.balance
        return t

    def get_account(self, acc_num: str) -> Account:
        for account in self.accounts:
            if account.id == int(acc_num):
                return account

    def new_transaction(self, bank: str, acc_num: str, to: str, comments: str, amount: float) -> bool:
        acc = self.get_account(acc_num)
        if acc.balance - amount < 0:
            return False
        else:
            try:
                t_json = {
                    "FromAcc": acc_num,
                    "ToAcc": to,
                    "Comments": comments,
                    "Amount": amount
                }
                ip = BANK_SERVERS[bank]
                trans = requests.post(f"https://{ip}/t/new", data=t_json, verify=False)
                return trans.json()["Transaction#"]
            except Exception as e:
                print(e)
                return False