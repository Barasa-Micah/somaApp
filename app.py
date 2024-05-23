import json
from flask import Flask, jsonify, request, abort, session
from db import app, mysql, init_db
from werkzeug.security import generate_password_hash, check_password_hash

app.secret_key = "commcomm"

# Ensure database and table exist
with app.app_context():
    init_db()


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


if __name__ == "__main__":
    app.run(debug=True)
