from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField,validators


class LoginForm(FlaskForm):
    uname = StringField("UserID", validators=[validators.DataRequired()])
    pw = PasswordField("Password", validators=[validators.DataRequired()])
    submit = SubmitField("Login", validators=[validators.DataRequired()])


class OTPForm(FlaskForm):
    otp = StringField("OTP", validators=[validators.DataRequired()])
    submit = SubmitField("Submit", validators=[validators.DataRequired()])


class RegisterForm(FlaskForm):
    uname = StringField("UserID", [validators.DataRequired()])
    email = StringField('Email Address', [validators.Email()])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    phone = StringField("Phone Number", [validators.DataRequired(),
                                         validators.Length(11, 11, message="Invalid Phone Number")])
    TOS = BooleanField("I accept the Terms of Service", [validators.DataRequired()])
    submit = SubmitField("Register", [validators.DataRequired()])


class SendForm(FlaskForm):
    fr = SelectField("Select Account", validate_choice=True, validators=[validators.DataRequired()])
    to = StringField("Beneficiary's Account", validators=[validators.DataRequired()])
    amount = StringField("Amount", validators=[validators.DataRequired()])
    comments = StringField("Comments")
    otp = StringField("Enter OTP", validators=[validators.DataRequired()])
    submit = SubmitField("Submit", [validators.DataRequired()])
