"""Configuración por entorno para Laboratorio de Inteligencia Pública V3.

Jerarquía:
    Base → Development → Production → Testing

Cada config hereda de Base y sobreescribe lo necesario.
"""
import os
from datetime import timedelta


class Config:
    """Configuración base. Compartida por todos los entornos."""

    SECRET_KEY: str = os.environ.get("SECRET_KEY", "dev-fallback-key-change-in-production")
    SQLALCHEMY_DATABASE_URI: str = os.environ.get(
        "DATABASE_URL",
        "postgresql://construyamos:construyamos@localhost:5432/construyamos_v3",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SQLALCHEMY_ENGINE_OPTIONS: dict = {
        "pool_size": 10,
        "max_overflow": 20,
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }

    # Sesiones
    PERMANENT_SESSION_LIFETIME: int = timedelta(hours=1).total_seconds()
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = "Lax"
    SESSION_COOKIE_NAME: str = "construyamos_session"

    # Seguridad
    WTF_CSRF_ENABLED: bool = True
    SEND_FILE_MAX_AGE_DEFAULT: int = 31536000  # 1 year for static files

    # Admin
    ADMIN_USER: str = os.environ.get("ADMIN_USER", "admin")
    ADMIN_PASS: str = os.environ.get("ADMIN_PASS", "admin")
    ADMIN_API_TOKEN: str = os.environ.get("ADMIN_API_TOKEN", "")

    # Rate limiting
    RATELIMIT_DEFAULT: str = "200 per day;50 per hour"
    RATELIMIT_STORAGE_URI: str = os.environ.get("RATELIMIT_STORAGE_URI", "memory://")

    # Cache
    CACHE_TYPE: str = os.environ.get("CACHE_TYPE", "SimpleCache")
    CACHE_REDIS_URL: str = os.environ.get("CACHE_REDIS_URL", "redis://localhost:6379/1")
    CACHE_DEFAULT_TIMEOUT: int = 300  # 5 minutos

    # SSL
    PREFERRED_URL_SCHEME: str = os.environ.get("PREFERRED_URL_SCHEME", "https")

    # Script prefix for reverse proxy (V3 runs at /v3/)
    SCRIPT_NAME: str = os.environ.get("SCRIPT_NAME", "")

    # Puerto de la app
    PORT: int = int(os.environ.get("PORT", 8000))

    # Plan estratégico activo por defecto
    PLAN_ACTIVO_ID: int = int(os.environ.get("PLAN_ACTIVO_ID", 1))


class DevelopmentConfig(Config):
    """Configuración para desarrollo local."""

    DEBUG: bool = True
    SQLALCHEMY_DATABASE_URI: str = os.environ.get(
        "DATABASE_URL",
        "sqlite:///construyamos_v3.db",
    )
    CACHE_TYPE: str = "SimpleCache"


class ProductionConfig(Config):
    """Configuración para producción."""

    DEBUG: bool = False
    SESSION_COOKIE_SECURE: bool = True
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = "Lax"
    PROPAGATE_EXCEPTIONS: bool = False
    RATELIMIT_STORAGE_URI: str = os.environ.get("RATELIMIT_STORAGE_URI", "memory://")
    CACHE_TYPE: str = os.environ.get("CACHE_TYPE", "RedisCache")
    CACHE_REDIS_URL: str = os.environ.get("CACHE_REDIS_URL", "redis://localhost:6379/1")

    SQLALCHEMY_ENGINE_OPTIONS: dict = {
        "pool_size": 10,
        "max_overflow": 20,
        "pool_recycle": 300,
        "pool_pre_ping": True,
        "pool_timeout": 30,
    }


class TestingConfig(Config):
    """Configuración para testing."""

    TESTING: bool = True
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///:memory:"
    CACHE_TYPE: str = "SimpleCache"
    WTF_CSRF_ENABLED: bool = False


config: dict[str, type[Config]] = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
