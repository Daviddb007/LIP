import os
from datetime import timedelta


class Config:
    """Base configuration with environment variable loading."""

    SECRET_KEY: str = os.environ.get('SECRET_KEY', 'dev-fallback-key-change-in-production')
    SQLALCHEMY_DATABASE_URI: str = os.environ.get(
        'DATABASE_URL',
        'postgresql://postgres:postgres@localhost:5432/construyamos_colombia',
    )
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    PERMANENT_SESSION_LIFETIME: timedelta = timedelta(hours=1)
    ADMIN_USER: str = os.environ.get('ADMIN_USER', 'admin')
    ADMIN_PASS: str = os.environ.get('ADMIN_PASS', 'admin')
    PREFERRED_URL_SCHEME: str = os.environ.get('PREFERRED_URL_SCHEME', 'https')

    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = 'Lax'


class DevelopmentConfig(Config):
    """Development configuration with SQLite default."""

    DEBUG: bool = True
    SQLALCHEMY_DATABASE_URI: str = os.environ.get(
        'DATABASE_URL', 'sqlite:///construyamos_colombia.db'
    )
    CACHE_TYPE: str = 'SimpleCache'


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG: bool = False
    SESSION_COOKIE_SECURE: bool = True
    PROPAGATE_EXCEPTIONS: bool = False
    RATELIMIT_STORAGE_URI: str = os.environ.get(
        'RATELIMIT_STORAGE_URI', 'memory://'
    )
    CACHE_TYPE: str = os.environ.get('CACHE_TYPE', 'RedisCache')
    CACHE_REDIS_URL: str = os.environ.get('CACHE_REDIS_URL', 'redis://localhost:6379/1')
    SQLALCHEMY_ENGINE_OPTIONS: dict = {
        'pool_size': 10,
        'max_overflow': 20,
        'pool_recycle': 300,
        'pool_pre_ping': True,
        'pool_timeout': 30,
    }


class TestingConfig(Config):
    """Testing configuration with in-memory database."""

    TESTING: bool = True
    SQLALCHEMY_DATABASE_URI: str = 'sqlite:///:memory:'
    CACHE_TYPE: str = 'SimpleCache'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig,
}
