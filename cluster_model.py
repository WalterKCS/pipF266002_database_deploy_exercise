"""Nearest-centroid labels from the k=3 skill model. Centroids are plain numbers."""

# Order: skill_programming, skill_data_stats, skill_frontend_design, skill_business_pitch.
CENTROIDS = [
    (2.923076923076923, 3.0769230769230766, 2.8461538461538463, 4.0),
    (3.0, 3.6, 1.4, 1.5999999999999996),
    (4.2, 4.6, 4.0, 4.6),
]


def predict_cluster(skills):
    """Return the index of the centroid closest to the four skill ratings."""
    best_label = 0
    best_distance = None
    for label, centroid in enumerate(CENTROIDS):
        distance = sum((float(score) - center) ** 2 for score, center in zip(skills, centroid))
        if best_distance is None or distance < best_distance:
            best_distance = distance
            best_label = label
    return best_label


if __name__ == "__main__":
    import csv
    from pathlib import Path

    path = Path(__file__).resolve().parent / "class_dataset.csv"
    skill_columns = [
        "skill_programming",
        "skill_data_stats",
        "skill_frontend_design",
        "skill_business_pitch",
    ]
    matches = 0
    total = 0
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            skills = [row[column] for column in skill_columns]
            predicted = predict_cluster(skills)
            total += 1
            if predicted == int(row["cluster"]):
                matches += 1
    print(f"{matches} of {total} students match the k-means labels")
