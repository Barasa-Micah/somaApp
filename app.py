from flask import Flask, jsonify, request, abort, session, url_for, render_template
from db import app, mysql, init_db
from werkzeug.security import generate_password_hash, check_password_hash
from mail import mail, generate_reset_token, send_reset_email
from itsdangerous import URLSafeTimedSerializer
import os
import dotenv
from flask_moment import Moment
import datetime

app.secret_key = os.getenv("SECRET_KEY")

# Ensure database and table exist
with app.app_context():
    init_db()
moment = Moment(app)


@app.route("/")
def users():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, username, email FROM Users")
    users = cursor.fetchall()
    cursor.close()
    return jsonify(users)


@app.route("/register", methods=["POST"])
def register():
    if not request.json or not all(
        key in request.json for key in ("username", "email", "password")
    ):
        abort(400)
    username = request.json["username"]
    email = request.json["email"]
    password = request.json["password"]

    hashed_password = generate_password_hash(password)
    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO Users(username, email, password) VALUES (%s, %s, %s)",
            (username, email, hashed_password),
        )
        mysql.connection.commit()
        cursor.close()
        return "OK", 201
    except Exception as e:
        return str(e)


@app.route("/login", methods=["POST"])
def login():
    if not request.json or not all(
        key in request.json for key in ("email", "password")
    ):
        abort(400)
    email = request.json["email"]
    password = request.json["password"]

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Users WHERE email=%s", (email,))
    user = cursor.fetchone()
    cursor.close()

    if user and check_password_hash(user["password"], password):
        session["loggedin"] = True
        session["id"] = user["id"]
        session["username"] = user["username"]
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"message": "Invalid email or password"}), 401


@app.route("/forgot", methods=["POST"])
def forgot():
    email = request.json.get("email")
    if not email:
        return jsonify({"message": "Email is required."}), 400

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Users WHERE email=%s", (email,))
    user = cur.fetchone()
    cur.close()

    if user:
        token = generate_reset_token(email)
        send_reset_email(email, token)

        return jsonify(
            {"message": "A password reset link has been sent to your email address."}
        )
    else:
        return jsonify({"message": "Email not found."})


@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_token(token):
    try:
        s = URLSafeTimedSerializer(app.secret_key)
        email = s.loads(token, salt="password-reset-salt", max_age=3600)
    except:
        return jsonify({"message": "The reset link is invalid or has expired."})

    if request.method == "POST":
        password = request.form["password"]
        hashed_password = generate_password_hash(password)

        cursor = mysql.connection.cursor()
        cursor.execute(
            "UPDATE Users SET password=%s WHERE email=%s", (hashed_password, email)
        )
        mysql.connection.commit()
        cursor.close()
        return jsonify({"message": "Your password has been updated."})

    return render_template("reset_password.html")


if __name__ == "__main__":
    app.run(debug=True)
