"""Run starter queries against the class intake database.

Add a (title, sql) pair to QUERIES to try something new, then:

    python query.py
"""

import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent

QUERIES = [
    (
        "Student count (should match CSV row count)",
        "SELECT COUNT(*) AS n FROM students;",
    ),
    (
        "Sample names and school years",
        "SELECT name, school_year FROM students LIMIT 5;",
    ),
    (
        "How many students listed each tool",
        """
        SELECT t.name, COUNT(*) AS n_students
        FROM student_tools st
        JOIN tools t ON st.tool_id = t.id
        GROUP BY t.name
        ORDER BY n_students DESC;
        """,
    ),
    (
        "How many students are free in each time slot",
        """
        SELECT a.label, COUNT(*) AS n_students
        FROM student_availability sa
        JOIN availability_slots a ON sa.slot_id = a.id
        GROUP BY a.label
        ORDER BY n_students DESC;
        """,
    ),
    (
        "Average self-reported skills by school year",
        """
        SELECT
            school_year,
            ROUND(AVG(skill_programming), 2) AS avg_programming,
            ROUND(AVG(skill_data_stats), 2) AS avg_data_stats,
            ROUND(AVG(skill_frontend_design), 2) AS avg_frontend,
            ROUND(AVG(skill_business_pitch), 2) AS avg_pitch,
            COUNT(*) AS n
        FROM students
        GROUP BY school_year
        ORDER BY n DESC;
        """,
    ),
    (
        "Students with missing working_style",
        """
        SELECT netid, name
        FROM students
        WHERE working_style IS NULL;
        """,
    ),
]


def print_result(cursor):
    columns = [col.name for col in cursor.description]
    rows = cursor.fetchall()
    print("  " + " | ".join(columns))
    if not rows:
        print("  (no rows)")
        return
    for row in rows:
        print("  " + " | ".join(str(value) for value in row))


def main():
    load_dotenv(ROOT / ".env")
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise SystemExit("DATABASE_URL is not set in .env")

    conn = psycopg2.connect(database_url)
    try:
        with conn.cursor() as cur:
            for i, (title, sql) in enumerate(QUERIES, start=1):
                print(f"\n[{i}] {title}")
                cur.execute(sql)
                print_result(cur)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
