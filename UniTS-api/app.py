from __future__ import annotations
from flask import Flask, request, flash, redirect, url_for, session, render_template, get_flashed_messages
from flask_bootstrap import Bootstrap
from flask_restful import Api
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_qrcode import QRcode
from json import dumps
from resources import *
from forms import LoginForm, OTPForm, RegisterForm, SendForm
from auth import User, register_user, user_exists
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = "I am a string"
api = Api(app)
bootstrap = Bootstrap(app)

log_mgr = LoginManager()
log_mgr.init_app(app)
log_mgr.login_view = "login"

qrcode = QRcode(app)

api.add_resource(Accounts, "/a/<acc_num>")
api.add_resource(Transactions, "/ts/<acc_num>")
api.add_resource(R_Transaction, "/t/<trans_num>", "/t/new")


@log_mgr.user_loader
def load_user(user):
    return User(user)


@app.before_request
def before_request():
    if request.url.startswith('http://'):
        url = request.url.replace('http://', 'https://', 1)
        code = 301
        return redirect(url, code=code)


@app.route("/", methods=["POST", "GET"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User(form.uname.data)
        if user is not None:
            if user.check_pw(form.pw.data):
                login_user(user)
                user.generate_otp()
                return redirect("/otp")
            else:
                flash('Invalid username or password')
                return redirect("/")
        else:
            flash('Invalid username or password')
            return redirect("/")

    return render_template('login.html', title='Log In', form=form)


@app.route("/otp", methods=["POST", "GET"])
def otp():
    form = OTPForm()
    if form.validate_on_submit():
        status, message = current_user.check_otp(form.otp.data)
        if status:
            session["user"] = current_user.user
            return redirect('/main')
        else:
            flash("Invalid OTP")
    return render_template('otp.html', title='Log In', form=form)


@app.route("/register", methods=["POST", "GET"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        result = user_exists(form.uname.data, form.phone.data, form.email.data)
        if result[0]:
            flash(result[1])
            return render_template('register.html', title='Log In', form=form)
        else:
            register_user(form.uname.data, form.password.data, form.phone.data, form.email.data)
            user = User(form.uname.data)
            login_user(user)
            user.generate_otp()
            return redirect("/otp")
    return render_template('register.html', title='Log In', form=form)


@app.route('/main', methods=["GET"])
@login_required
def main():
    if current_user.user == session["user"]:
        current_user.update_accounts()
        return render_template("main.html")
    else:
        return redirect("/")


@app.route('/accounts', methods=["GET"])
@login_required
def account():
    if current_user.user == session["user"]:
        current_user.update_accounts()
        return render_template("accounts.html")
    else:
        return redirect("/")


@app.route('/accounts/<acc_num>', methods=["GET"])
@login_required
def v_account(acc_num):
    if current_user.user == session["user"]:
        current_user.update_accounts()
        acc = current_user.get_account(acc_num)
        return render_template("account.html", acc=acc)
    else:
        return redirect("/")


@app.route('/transaction/<acc_num>/<tran_num>', methods=["GET"])
@login_required
def transaction(acc_num, tran_num):
    if current_user.user == session["user"]:
        current_user.update_accounts()
        acc = current_user.get_account(acc_num)
        trans = acc.get_transaction(tran_num)
        print(trans._comments)
        return render_template("transaction.html", trans=trans)
    else:
        return redirect("/")


@app.route('/send/<o>', methods=["GET", "POST"])
@login_required
def send(o):
    if current_user.user == session["user"]:
        if check_password_hash(o, session["user"]):
            current_user.generate_otp()
        current_user.update_accounts()
        lst = []
        for acc in current_user.accounts:
            s = f"{acc.bank} {str(acc.id)}"
            lst.append(s)
        form = SendForm()
        form.fr.choices = lst
        if form.validate_on_submit():
            try:
                amount = abs(float(form.amount.data))
            except ValueError as e:
                flash("Amount must be an number")
                return render_template("send.html", form=form, hsh=generate_password_hash(session["user"]))
            status, message = current_user.check_otp(form.otp.data)
            if not status:
                flash("The OTP was incorrect!")
                return render_template("send.html", form=form, hsh=generate_password_hash(session["user"]))
            bank = form.fr.data.split()[0]
            fr = form.fr.data.split()[1]
            result = current_user.new_transaction(bank, fr, form.to.data, form.comments.data, amount)
            if result:
                flash("The transaction was successful!")
                return redirect(f"/transaction/{fr}/{result}")
            else:
                flash("Your transaction could not be processed")
                return render_template("send.html", form=form, hsh=generate_password_hash(session["user"]))
        return render_template("send.html", form=form, hsh=generate_password_hash(session["user"]))

    else:
        return redirect("/")


@app.route('/account/add', methods=["GET"])
@login_required
def add_account():
    if current_user.user == session["user"]:
        code = generate_password_hash(current_user.user)
        return render_template("new_account.html", code=code)
    else:
        return redirect("/")


@app.route('/logout', methods=["GET"])
@login_required
def logout():
    logout_user()
    del session["user"]
    flash("Logout Successful!")
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, ssl_context='adhoc', debug=False)
