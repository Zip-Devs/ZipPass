import base64
import hashlib
from cryptography.fernet import Fernet

def derive_key(master_password: str) -> bytes:
    hash_bytes = hashlib.sha256(master_password.encode()).digest()
    return base64.urlsafe_b64encode(hash_bytes)

def encrypt(data: bytes, password: str) -> bytes:
    return Fernet(derive_key(password)).encrypt(data)

def decrypt(data: bytes, password: str) -> bytes:
    return Fernet(derive_key(password)).decrypt(data)
