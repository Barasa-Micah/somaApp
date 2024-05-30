from flask_mysqldb import MySQL
from flask import Flask
import MySQLdb
import os
import dotenv

app = Flask(__name__)

# MySQL configuration using hard-coded credentials
app.config["MYSQL_HOST"] =os.getenv("MYSQL_HOST")
app.config["MYSQL_USER"] = os.getenv("MYSQL_USER")
app.config["MYSQL_PASSWORD"] = os.getenv("MYSQL_PASSWORD")
app.config["MYSQL_DB"] = os.getenv("MYSQL_DB")
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)


def init_db():
    with app.app_context():
        # Connect to MySQL server to create the database
        db = MySQLdb.connect(
            host=app.config["MYSQL_HOST"],
            user=app.config["MYSQL_USER"],
            passwd=app.config["MYSQL_PASSWORD"],
        )
        cursor = db.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS myproject")
        db.commit()
        cursor.close()
        db.close()

        # Now connect using the app configuration to create the tables
        cursor = mysql.connection.cursor()
        cursor.execute("USE myproject")
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Users(
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL,
                email VARCHAR(50) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL
            )
            """
        )
        mysql.connection.commit()
        cursor.close()


def dbconnection():
    return mysql


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
