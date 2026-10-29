"""Flask API: class roster from Railway Postgres."""

import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "frontend" / "dist"

load_dotenv(ROOT / ".env")

app = Flask(__name__)
CORS(app)


def get_connection():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set")
    return psycopg2.connect(database_url)


@app.get("/api/students")
def list_students():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT netid, name, school_year
                FROM students
                ORDER BY name
                """
            )
            students = [
                {"netid": netid, "name": name, "school_year": school_year}
                for netid, name, school_year in cur.fetchall()
            ]
        return jsonify(students)
    finally:
        conn.close()


@app.get("/")
def index():
    return send_from_directory(DIST, "index.html")


@app.get("/<path:path>")
def static_file(path):
    file_path = DIST / path
    if file_path.is_file():
        return send_from_directory(DIST, path)
    return send_from_directory(DIST, "index.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
