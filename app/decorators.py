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

    Only trusts X-Forwarded-For when behind a known proxy.
    Falls back to remote_addr which is harder to spoof.
    """
    if request.remote_addr:
        return request.remote_addr
    return 'unknown'


def hash_ip(ip_address: str) -> str:
    """SHA-256 hash of the client IP for anonymized storage."""
    return hashlib.sha256(ip_address.encode()).hexdigest()
