from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
import sqlite3
import string
import random
import re
from models import init_db
import os
app = Flask(__name__)
CORS(app)

DB_NAME = "database.db"

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:5000")

init_db()


# 🔹 Generate random code
def generate_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


# 🔹 Ensure unique short code
def generate_unique_code():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    while True:
        code = generate_code()
        cursor.execute("SELECT id FROM urls WHERE short_code=?", (code,))
        if not cursor.fetchone():
            conn.close()
            return code


# 🔹 Validate URL
def is_valid_url(url):
    regex = re.compile(
        r'^(https?:\/\/)?([\w\-]+\.)+[a-zA-Z]{2,63}'
    )
    return re.match(regex, url)


# 🔹 DB connection
def get_db():
    return sqlite3.connect(DB_NAME)


@app.route("/shorten", methods=["POST"])
def shorten_url():
    data = request.get_json()
    original_url = data.get("original_url")

    if not original_url or not is_valid_url(original_url):
        return jsonify({"error": "Invalid URL"}), 400

    # Add http if missing
    if not original_url.startswith("http"):
        original_url = "http://" + original_url

    short_code = generate_unique_code()
    short_url = f"{BASE_URL}/{short_code}"

    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO urls (original_url, short_code) VALUES (?, ?)",
            (original_url, short_code)
        )

        conn.commit()
        conn.close()

        return jsonify({
            "original_url": original_url,
            "short_url": short_url,
            "clicks": 0
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/<code>")
def redirect_url(code):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT original_url, clicks FROM urls WHERE short_code=?",
        (code,)
    )
    result = cursor.fetchone()

    if result:
        original_url, clicks = result

        cursor.execute(
            "UPDATE urls SET clicks=? WHERE short_code=?",
            (clicks + 1, code)
        )
        conn.commit()
        conn.close()

        return redirect(original_url)

    conn.close()
    return "URL not found", 404


@app.route("/dashboard")
def dashboard():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT original_url, short_code, clicks, created_at FROM urls ORDER BY created_at DESC"
    )
    rows = cursor.fetchall()
    conn.close()

    data = []
    for row in rows:
        data.append({
            "original_url": row[0],
            "short_url": f"{BASE_URL}/{row[1]}",
            "clicks": row[2],
            "created_at": row[3]
        })

    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True)