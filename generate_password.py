"""Utilidad para generar hashes de contraseña para ADMIN_PASS.

Uso:
    python generate_password.py mi_contraseña
"""
import getpass
import sys
from hashlib import pbkdf2_hmac


def generate_hash(password: str) -> str:
    """Genera un hash pbkdf2:sha256 de la contraseña."""
    import base64
    import os

    salt = os.urandom(16)
    dk = pbkdf2_hmac("sha256", password.encode(), salt, 100000)
    return base64.b64encode(salt + dk).decode()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        password = sys.argv[1]
    else:
        password = getpass.getpass("Contraseña: ")

    hash_value = generate_hash(password)
    print(f"\nHash generado (copiar como ADMIN_PASS):")
    print(f"ADMIN_PASS={hash_value}")
