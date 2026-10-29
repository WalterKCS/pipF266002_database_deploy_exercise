"""Create the agreed schema and load class_dataset.csv into Postgres."""

import csv
from pathlib import Path

import psycopg2
from dotenv import load_dotenv
import os

ROOT = Path(__file__).resolve().parent
SCHEMA_PATH = ROOT / "schema.sql"
CSV_CANDIDATES = [
    ROOT / "data" / "class_dataset.csv",
    ROOT / "class_dataset.csv",
]

TABLES = [
    "students",
    "tools",
    "availability_slots",
    "student_tools",
    "student_availability",
]


def split_semicolon(value):
    if not value:
        return []
    return [part.strip() for part in value.split(";") if part.strip()]


def clean_text(value):
    if value is None:
        return None
    text = value.strip()
    if text == "" or text == "#NAME?":
        return None
    return text


def main():
    load_dotenv(ROOT / ".env")
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise SystemExit("DATABASE_URL is not set in .env")

    csv_path = next((path for path in CSV_CANDIDATES if path.exists()), None)
    if csv_path is None:
        raise SystemExit("CSV not found: data/class_dataset.csv or class_dataset.csv")
    if not SCHEMA_PATH.exists():
        raise SystemExit(f"Schema not found: {SCHEMA_PATH}")

    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
    print(f"Applying {SCHEMA_PATH.name} to Railway Postgres…")
    print(f"Loading {csv_path.relative_to(ROOT)}")

    conn = psycopg2.connect(database_url)
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DROP TABLE IF EXISTS student_availability CASCADE;
                    DROP TABLE IF EXISTS student_tools CASCADE;
                    DROP TABLE IF EXISTS availability_slots CASCADE;
                    DROP TABLE IF EXISTS tools CASCADE;
                    DROP TABLE IF EXISTS students CASCADE;
                    """
                )
                cur.execute(schema_sql)

                tool_ids = {}
                slot_ids = {}

                with csv_path.open(newline="", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        cur.execute(
                            """
                            INSERT INTO students (
                                netid, name, school_year, intro_programming,
                                skill_programming, skill_data_stats,
                                skill_frontend_design, skill_business_pitch,
                                working_style, interests, semester_goal, submitted_at
                            ) VALUES (
                                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                            )
                            """,
                            (
                                row["netid"].strip(),
                                row["name"].strip(),
                                row["school_year"].strip(),
                                row["intro_programming"].strip(),
                                int(row["skill_programming"]),
                                int(row["skill_data_stats"]),
                                int(row["skill_frontend_design"]),
                                int(row["skill_business_pitch"]),
                                clean_text(row["working_style"]),
                                clean_text(row["interests"]),
                                clean_text(row["semester_goal"]),
                                row["submitted_at"].strip(),
                            ),
                        )
                        netid = row["netid"].strip()

                        for tool_name in split_semicolon(row["tools"]):
                            if tool_name not in tool_ids:
                                cur.execute(
                                    """
                                    INSERT INTO tools (name) VALUES (%s)
                                    ON CONFLICT (name) DO NOTHING
                                    """,
                                    (tool_name,),
                                )
                                cur.execute(
                                    "SELECT id FROM tools WHERE name = %s",
                                    (tool_name,),
                                )
                                tool_ids[tool_name] = cur.fetchone()[0]
                            cur.execute(
                                """
                                INSERT INTO student_tools (netid, tool_id)
                                VALUES (%s, %s)
                                ON CONFLICT DO NOTHING
                                """,
                                (netid, tool_ids[tool_name]),
                            )

                        for slot_label in split_semicolon(row["availability"]):
                            if slot_label not in slot_ids:
                                cur.execute(
                                    """
                                    INSERT INTO availability_slots (label)
                                    VALUES (%s)
                                    ON CONFLICT (label) DO NOTHING
                                    """,
                                    (slot_label,),
                                )
                                cur.execute(
                                    "SELECT id FROM availability_slots WHERE label = %s",
                                    (slot_label,),
                                )
                                slot_ids[slot_label] = cur.fetchone()[0]
                            cur.execute(
                                """
                                INSERT INTO student_availability (netid, slot_id)
                                VALUES (%s, %s)
                                ON CONFLICT DO NOTHING
                                """,
                                (netid, slot_ids[slot_label]),
                            )

                print("Row counts:")
                for table in TABLES:
                    cur.execute(f"SELECT COUNT(*) FROM {table}")
                    print(f"  {table}: {cur.fetchone()[0]}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
