"""App factory para Construyamos Colombia V3.

Inicializa la aplicación Flask con todas las extensiones,
blueprints, error handlers y hooks de request.
"""
from __future__ import annotations

import gzip
import logging
import time
from io import BytesIO
from logging.handlers import RotatingFileHandler

from flask import Flask, g, request
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

from config import config

# Extensiones (singletons a nivel de módulo)
db = SQLAlchemy()
migrate = Migrate()
limiter = Limiter(key_func=get_remote_address)
cache = Cache()
csrf = CSRFProtect()


def create_app(config_name: str = "default") -> Flask:
    """Factory principal. Crea, configura y retorna la app Flask."""

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    _configure_logging(app)
    _register_url_prefix(app)
    _init_extensions(app)
    _register_blueprints(app)
    _register_error_handlers(app)
    _register_request_hooks(app)

    return app


def _configure_logging(app: Flask) -> None:
    """Configura logging con RotatingFileHandler en producción."""
    log_level = getattr(logging, app.config.get("LOG_LEVEL", "INFO").upper(), logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Stream handler (siempre)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(log_level)
    app.logger.addHandler(stream_handler)
    app.logger.setLevel(log_level)

    # File handler (solo en producción)
    if not app.debug and not app.testing:
        file_handler = RotatingFileHandler(
            "app.log", maxBytes=10 * 1024 * 1024, backupCount=10
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.WARNING)
        app.logger.addHandler(file_handler)

    app.logger.info("App iniciada en modo %s", app.config.get("FLASK_CONFIG", "default"))


def _init_extensions(app: Flask) -> None:
    """Inicializa todas las extensiones Flask."""
    db.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)
    cache.init_app(app)
    csrf.init_app(app)


def _register_blueprints(app: Flask) -> None:
    """Registra todos los blueprints de la aplicación."""
    from app.routes.home import home_bp
    from app.routes.participar import participar_bp
    from app.routes.iniciativa import iniciativa_bp
    from app.routes.resultados import resultados_bp
    from app.routes.admin import admin_bp
    from app.routes.health import health_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(participar_bp)
    app.register_blueprint(iniciativa_bp)
    app.register_blueprint(resultados_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(health_bp)


def _register_error_handlers(app: Flask) -> None:
    """Registra handlers de errores personalizados."""
    from app.errors import register_error_handlers

    register_error_handlers(app)


def _register_request_hooks(app: Flask) -> None:
    """Registra hooks before_request / after_request para logging de timing y seguridad."""

    @app.before_request
    def before_request():
        g.start_time = time.time()

    @app.after_request
    def after_request(response):
        if hasattr(g, "start_time"):
            elapsed = time.time() - g.start_time
            app.logger.info(
                "%s %s %s %.3fs",
                request.method,
                request.path,
                response.status_code,
                elapsed,
            )

        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        if not app.debug:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # Gzip compression for text responses
        accept_encoding = request.headers.get("Accept-Encoding", "")
        if "gzip" in accept_encoding and response.content_type:
            text_types = ("text/", "application/json", "application/javascript")
            if any(response.content_type.startswith(t) for t in text_types):
                original_data = response.get_data(as_text=True)
                compressed = gzip.compress(original_data.encode("utf-8"), compresslevel=5)
                if len(compressed) < len(original_data):
                    response.set_data(compressed)
                    response.headers["Content-Encoding"] = "gzip"
                    response.headers["Content-Length"] = len(compressed)
                    response.vary = "Accept-Encoding"

        return response


def _register_url_prefix(app: Flask) -> None:
    """Override url_for to prepend /v3/ prefix for reverse proxy routing.

    Patches both the Jinja2 template global and the Python-level
    flask.url_for so redirects and internal calls also get the prefix.
    """
    import flask

    _original_url_for = flask.url_for

    def _prefixed_url_for(endpoint: str, **values: object) -> str:
        url = _original_url_for(endpoint, **values)
        prefix = "/v3"
        if url.startswith("http://") or url.startswith("https://"):
            # External URL — insert prefix after the host
            from urllib.parse import urlparse, urlunparse
            parsed = urlparse(url)
            new_path = prefix + parsed.path
            url = urlunparse(parsed._replace(path=new_path))
        elif not url.startswith(prefix) and url.startswith("/"):
            url = prefix + url
        return url

    # Patch the module-level function used in Python code
    flask.url_for = _prefixed_url_for

    # Patch the Jinja2 global used in templates
    app.jinja_env.globals["url_for"] = _prefixed_url_for

    @app.context_processor
    def _url_for_context():
        return dict(url_for=_prefixed_url_for)
