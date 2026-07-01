"""Utility script to generate hashed passwords for ADMIN_PASS config.

Usage:
    python generate_password.py <password>

Generates a pbkdf2:sha256 hash suitable for use in ADMIN_PASS environment variable.
"""

import sys
from werkzeug.security import generate_password_hash


def main() -> None:
    if len(sys.argv) < 2:
        print('Usage: python generate_password.py <password>')
        sys.exit(1)

    password = sys.argv[1]
    hashed = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
    print(f'Hashed password: {hashed}')
    print(f'\nSet this in your .env file:')
    print(f'ADMIN_PASS={hashed}')


if __name__ == '__main__':
    main()
