from flask_mail import Mail, Message
from db import app
from itsdangerous import URLSafeTimedSerializer
from flask import url_for
import re
import os
import dotenv

app.config["MAIL_SERVER"] = "smtp.googlemail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_USERNAME")


mail = Mail(app)


def generate_reset_token(email):
    s = URLSafeTimedSerializer(app.secret_key)
    reset_token = s.dumps(email, salt="password-reset-salt")
    return reset_token


def is_valid_email(email):
    regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(regex, email)


def send_reset_email(email, token):
    if not email or not is_valid_email(email):
        return



    msg = Message(
        "Password Reset Request", 
        recipients=[email],
        body = f"""To reset your password, visit the following link:
        {url_for('reset_token', token=token, _external=True)}
        If you did not make this request then simply ignore this email and no changes will be made.
        """
    )

    mail.send(msg)
    return "Email sent" ,200
