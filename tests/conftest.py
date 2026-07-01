from __future__ import annotations

import pytest

from app import create_app, db as _db
from app.seed import seed_database


@pytest.fixture(scope='session')
def app():
    """Create application for testing."""
    app = create_app('testing')
    with app.app_context():
        _db.create_all()
        seed_database()
        yield app
        _db.drop_all()


@pytest.fixture(scope='function')
def db(app):
    """Provide a clean database session for each test."""
    with app.app_context():
        _db.session.begin_nested()
        yield _db
        _db.session.rollback()


@pytest.fixture(scope='function')
def client(app):
    """Provide a test client."""
    return app.test_client()


@pytest.fixture(scope='function')
def logged_in_client(client, app):
    """Provide a test client with admin session active."""
    with app.app_context():
        from app.forms import LoginForm
        from flask_wtf.csrf import generate_csrf

        with client.session_transaction() as sess:
            sess['admin_logged_in'] = True

    return client
