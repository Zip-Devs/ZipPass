from __future__ import annotations

import json
import os
from typing import Any

from cryptography.fernet import Fernet, InvalidToken

# =====================
# ZipPass file format
# =====================

MAGIC = b"ZIPPASS"
VERSION = b"\x01"
HEADER_SIZE = len(MAGIC) + len(VERSION)


# =====================
# Crypto helpers
# =====================

def _derive_key(master_password: str) -> bytes:
    """
    IMPORTANT:
    You already have this logic in your project (crypto.py).
    If you use a different key derivation, KEEP IT.
    This is only a placeholder call site.
    """
    from core.crypto import derive_key
    return derive_key(master_password)


# =====================
# Vault API
# =====================

def save_vault(vault: dict, master_password: str, path: str | None = None) -> None:
    """
    Save vault to .zippass file with header.
    """
    if path is None:
        path = _default_vault_path()

    key = _derive_key(master_password)
    fernet = Fernet(key)

    payload = json.dumps(vault, ensure_ascii=False).encode("utf-8")
    encrypted = fernet.encrypt(payload)

    with open(path, "wb") as f:
        f.write(MAGIC)
        f.write(VERSION)
        f.write(encrypted)


def load_vault(master_password: str, path: str | None = None) -> dict:
    """
    Load vault from .zippass file.
    Validates header BEFORE decrypting.
    """
    if path is None:
        path = _default_vault_path()

    with open(path, "rb") as f:
        header = f.read(HEADER_SIZE)
        data = f.read()

    # ---- Header validation ----
    if not header.startswith(MAGIC):
        raise ValueError("Not a ZipPass vault file")

    version = header[len(MAGIC):]
    if version != VERSION:
        raise ValueError(f"Unsupported ZipPass vault version: {version!r}")

    key = _derive_key(master_password)
    fernet = Fernet(key)

    try:
        decrypted = fernet.decrypt(data)
    except InvalidToken:
        raise ValueError("Invalid master password or corrupted vault")

    vault = json.loads(decrypted.decode("utf-8"))
    _validate_vault(vault)
    return vault


# =====================
# Helpers
# =====================

def _default_vault_path() -> str:
    """
    Default vault location.
    Can be replaced later by file picker / multi-vault.
    """
    os.makedirs("data", exist_ok=True)
    return os.path.join("data", "default.zippass")


def _validate_vault(vault: Any) -> None:
    """
    Minimal structural validation.
    """
    if not isinstance(vault, dict):
        raise ValueError("Invalid vault structure")

    if "entries" not in vault or "categories" not in vault:
        raise ValueError("Invalid vault format")

    if not isinstance(vault["entries"], list):
        raise ValueError("Invalid entries format")

    if not isinstance(vault["categories"], list):
        raise ValueError("Invalid categories format")
