import csv
import time
import uuid


FIELDNAMES = [
    "id",
    "service",
    "login",
    "password",
    "url",
    "category_id",
    "note",
    "created_at",
    "updated_at",
]


def export_to_csv(entries: list, filepath: str):
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()

        for e in entries:
            writer.writerow({
                "id": e.get("id"),
                "service": e.get("service", ""),
                "login": e.get("login", ""),
                "password": e.get("password", ""),
                "url": e.get("url", ""),
                "category_id": e.get("category_id", "all"),
                "note": e.get("note", ""),
                "created_at": e.get("created_at", ""),
                "updated_at": e.get("updated_at", ""),
            })


def import_from_csv(filepath: str) -> list:
    entries = []

    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            now = time.time()

            entry = {
                "id": row.get("id") or str(uuid.uuid4()),
                "service": row.get("service", ""),
                "login": row.get("login", ""),
                "password": row.get("password", ""),
                "url": row.get("url", ""),
                "category_id": row.get("category_id") or "all",
                "note": row.get("note", ""),
                "created_at": float(row.get("created_at") or now),
                "updated_at": float(row.get("updated_at") or now),
            }

            entries.append(entry)

    return entries
