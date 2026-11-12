"""Assign students to groups by dealing cluster lists round-robin."""

import csv
from collections import defaultdict
from pathlib import Path

from cluster_model import predict_cluster

SKILL_COLUMNS = [
    "skill_programming",
    "skill_data_stats",
    "skill_frontend_design",
    "skill_business_pitch",
]

ROOT = Path(__file__).resolve().parent


def assign_groups(students, n_groups=8):
    """Return each student's id, cluster, and group.

    Clusters are ordered from most students to fewest, and students are
    sorted by id inside a cluster. That sequence is dealt to groups 1
    through n_groups, and the count continues across clusters.
    """
    labeled = []
    for student in students:
        if "skills" in student:
            skills = student["skills"]
        else:
            skills = [student[column] for column in SKILL_COLUMNS]
        labeled.append(
            {
                "id": student["id"],
                "cluster": predict_cluster(skills),
            }
        )

    by_cluster = defaultdict(list)
    for student in labeled:
        by_cluster[student["cluster"]].append(student)
    for members in by_cluster.values():
        members.sort(key=lambda student: student["id"])

    cluster_order = sorted(
        by_cluster,
        key=lambda cluster: (-len(by_cluster[cluster]), cluster),
    )
    deal = []
    for cluster in cluster_order:
        deal.extend(by_cluster[cluster])
    for index, student in enumerate(deal):
        student["group"] = (index % n_groups) + 1
    return labeled


def load_students(path):
    students = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            student = {"id": row["netid"]}
            for column in SKILL_COLUMNS:
                student[column] = row[column]
            students.append(student)
    return students


def main():
    assignments = assign_groups(load_students(ROOT / "class_dataset.csv"))
    clusters = sorted({student["cluster"] for student in assignments})
    groups = sorted({student["group"] for student in assignments})

    missing = 0
    for group in groups:
        members = [student for student in assignments if student["group"] == group]
        counts = {cluster: 0 for cluster in clusters}
        for student in members:
            counts[student["cluster"]] += 1
        breakdown = ", ".join(
            f"cluster {cluster}: {counts[cluster]}" for cluster in clusters
        )
        print(f"Group {group}: {len(members)} students ({breakdown})")
        if any(count == 0 for count in counts.values()):
            missing += 1
    print(f"Groups missing a cluster: {missing}")


if __name__ == "__main__":
    main()
