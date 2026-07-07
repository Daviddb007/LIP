from __future__ import annotations

import logging
import time
from logging.handlers import RotatingFileHandler

from flask import Flask, g, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache

from config import config

db = SQLAlchemy()
migrate = Migrate()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)
cache = Cache()


def create_app(config_name: str = 'default') -> Flask:
    """Application factory for creating Flask instances."""

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    _configure_logging(app)
    _init_extensions(app)
    _register_blueprints(app)
    _register_error_handlers(app)
    _register_request_hooks(app)

    return app


def _configure_logging(app: Flask) -> None:
    """Set up logging for the application with rotation."""
    log_level = logging.DEBUG if app.debug else logging.INFO
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    )

    if not app.debug and not app.testing:
        file_handler = RotatingFileHandler(
            'app.log', maxBytes=10_000_000, backupCount=10
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)
        app.logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(log_level)


def _init_extensions(app: Flask) -> None:
    """Initialize Flask extensions."""
    db.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)
    cache.init_app(app)

    storage_uri = app.config.get('RATELIMIT_STORAGE_URI', 'memory://')
    limiter.storage_uri = storage_uri


def _register_blueprints(app: Flask) -> None:
    """Register all application blueprints."""
    from app.routes.home import home_bp
    from app.routes.iniciativa import iniciativa_bp
    from app.routes.participar import participar_bp
    from app.routes.resultados import resultados_bp
    from app.routes.admin import admin_bp
    from app.routes.health import health_bp
    from app.routes.biblioteca import biblioteca_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(iniciativa_bp)
    app.register_blueprint(participar_bp)
    app.register_blueprint(resultados_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(health_bp)
    app.register_blueprint(biblioteca_bp)


def _register_error_handlers(app: Flask) -> None:
    """Register centralized error handlers."""
    from app.errors import register_error_handlers

    register_error_handlers(app)


def _register_request_hooks(app: Flask) -> None:
    """Register request/response logging hooks."""

    @app.before_request
    def before_request():
        g.start_time = time.time()

    @app.after_request
    def after_request(response):
        if hasattr(g, 'start_time'):
            elapsed = time.time() - g.start_time
            app.logger.info(
                '%s %s %s %.3fs',
                request.method,
                request.path,
                response.status_code,
                elapsed,
            )
        return response
