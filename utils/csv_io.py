import csv
import uuid
from pathlib import Path


# =========================
# Export (Brave / Chrome compatible)
# =========================

def export_to_csv(vault: dict, path: str) -> None:
    """
    Export vault entries to CSV compatible with Brave / Chrome.
    """
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["name", "url", "username", "password"]
        )
        writer.writeheader()

        for entry in vault.get("entries", []):
            writer.writerow({
                "name": entry.get("service", ""),
                "url": entry.get("url", ""),
                "username": entry.get("login", ""),
                "password": entry.get("password", ""),
            })


# =========================
# Import (ZipPass / Brave / Chrome)
# =========================

def import_from_csv(vault: dict, path: str) -> int:
    """
    Import entries from CSV into vault.
    Supports ZipPass, Brave, Chrome formats.
    Returns number of imported entries.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)

    # ---- ensure Imported category exists ----
    categories = vault.setdefault("categories", [])
    cat_map = {c["name"]: c["id"] for c in categories}

    imported_cat_id = cat_map.get("Imported")
    if not imported_cat_id:
        imported_cat_id = uuid.uuid4().hex
        categories.append({
            "id": imported_cat_id,
            "name": "Imported",
        })

    imported = 0

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            # ZipPass / Brave / Chrome mapping
            service = (
                row.get("service")
                or row.get("name")
                or ""
            ).strip()

            url = (row.get("url") or "").strip()
            login = (
                row.get("login")
                or row.get("username")
                or ""
            ).strip()
            password = row.get("password") or ""
            note = row.get("note", "").strip()

            if not service and not url:
                continue

            entry = {
                "id": uuid.uuid4().hex,
                "service": service or url,
                "login": login,
                "password": password,
                "url": url,
                "note": note,
                "category_id": imported_cat_id,
            }

            vault["entries"].append(entry)
            imported += 1

    return imported
