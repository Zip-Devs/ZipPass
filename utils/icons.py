from __future__ import annotations

import os
import urllib.request
from urllib.parse import urlparse

from PySide6.QtGui import QIcon

# =========================
# Config
# =========================

ICON_DIR = os.path.join("data", "icons")
TIMEOUT = 3


# =========================
# Utils
# =========================

def ensure_icon_dir() -> None:
    os.makedirs(ICON_DIR, exist_ok=True)


def normalize_domain(domain: str) -> str:
    """
    Normalize domain for favicon cache key.
    Removes common subdomains like www.
    """
    domain = domain.lower().strip()
    if domain.startswith("www."):
        domain = domain[4:]
    return domain


def extract_domain(url: str) -> str | None:
    if not url:
        return None

    if "://" not in url:
        url = "https://" + url

    try:
        parsed = urlparse(url)
        if not parsed.hostname:
            return None
        return normalize_domain(parsed.hostname)
    except Exception:
        return None


def icon_path_for_domain(domain: str) -> str:
    return os.path.join(ICON_DIR, f"{domain}.ico")


# =========================
# Download (explicit only)
# =========================

def download_favicon(domain: str) -> str | None:
    """
    Downloads favicon.ico for domain if not exists.
    BLOCKING. Call ONLY outside UI rendering.
    """
    ensure_icon_dir()
    path = icon_path_for_domain(domain)

    if os.path.exists(path):
        return path

    url = f"https://{domain}/favicon.ico"

    try:
        with urllib.request.urlopen(url, timeout=TIMEOUT) as resp:
            data = resp.read()

        # rudimentary validation
        if len(data) < 100:
            return None

        with open(path, "wb") as f:
            f.write(data)

        return path

    except Exception:
        return None


def ensure_favicon(url: str) -> None:
    """
    Ensures favicon exists in cache.
    Safe to call on add/import.
    """
    domain = extract_domain(url)
    if not domain:
        return

    path = icon_path_for_domain(domain)
    if os.path.exists(path):
        return

    download_favicon(domain)


# =========================
# Read-only (UI safe)
# =========================

def get_favicon(url: str) -> QIcon | None:
    """
    Returns cached favicon icon.
    NEVER downloads.
    Safe to call from model.data()
    """
    domain = extract_domain(url)
    if not domain:
        return None

    path = icon_path_for_domain(domain)
    if not os.path.exists(path):
        return None

    return QIcon(path)
