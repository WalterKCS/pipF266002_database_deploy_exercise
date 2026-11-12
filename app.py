"""Flask app: class roster from Railway Postgres, plus a single HTML page."""

import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv
from flask import Flask, jsonify, send_from_directory

ROOT = Path(__file__).resolve().parent
FRONTEND = ROOT / "frontend"

load_dotenv(ROOT / ".env")

app = Flask(__name__)


def get_connection():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set")
    if "sslmode=" not in database_url:
        joiner = "&" if "?" in database_url else "?"
        database_url = f"{database_url}{joiner}sslmode=require"
    return psycopg2.connect(database_url, connect_timeout=10)


@app.get("/api/students")
def list_students():
    try:
        conn = get_connection()
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 503
    except Exception:
        return jsonify({
            "error": (
                "Could not connect to the database. "
                "On the web service, set DATABASE_URL to the Postgres private URL."
            )
        }), 503

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
    return send_from_directory(FRONTEND, "index.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
