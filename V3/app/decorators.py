"""Decoradores y utilidades de seguridad para la app.

- login_required: protege rutas de admin
- get_client_ip: obtiene IP real del cliente (detrás de proxy)
- hash_ip: hashea IP con SHA-256 para anonimización
"""
from __future__ import annotations

import hashlib
import hmac
from functools import wraps

from flask import Request, session, redirect, request


def login_required(f):
    """Protege una ruta requiriendo sesión de admin activa.

    Para requests API/JSON retorna 401. Para browsers redirige al login.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("admin"):
            if request.is_json or request.path.startswith("/api/"):
                from app.errors import UnauthorizedError

                raise UnauthorizedError()
            from flask import url_for as _url_for
            return redirect(_url_for("admin.login"))
        return f(*args, **kwargs)

    return decorated_function


def get_client_ip() -> str:
    """Extrae la IP real del cliente, considerando proxies (X-Forwarded-For).

    Si hay múltiples IPs en X-Forwarded-For, usa la primera (la del cliente real).
    """
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.remote_addr or "unknown"


def hash_ip(ip_address: str) -> str:
    """Hashea una IP con SHA-256 para almacenamiento anonimizado.

    Usa una key derivada del SECRET_KEY de la app para hardening.
    """
    from flask import current_app

    key = current_app.config.get("SECRET_KEY", "default-key").encode()
    return hmac.new(key, ip_address.encode(), hashlib.sha256).hexdigest()
