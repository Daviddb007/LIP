from __future__ import annotations

import hashlib
from functools import wraps
from typing import Any, Callable

from flask import redirect, session, url_for, request, jsonify


def login_required(f: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator that requires an active admin session."""

    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        if 'admin_logged_in' not in session:
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({'error': 'Autenticación requerida'}), 401
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)

    return decorated_function


def get_client_ip() -> str:
    """Extract the real client IP with spoofing protection.

    Trusts X-Forwarded-For only when behind a known proxy (nginx).
    The first IP in the chain is the original client.
    """
    forwarded_for = request.headers.get('X-Forwarded-For')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    return request.remote_addr or 'unknown'


def hash_ip(ip_address: str) -> str:
    """SHA-256 hash of the client IP for anonymized storage."""
    return hashlib.sha256(ip_address.encode()).hexdigest()
