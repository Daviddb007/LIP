"""Fixtures de pytest para testing de la app V3."""
import pytest

from app import create_app, db as _db


@pytest.fixture(scope="session")
def app():
    app = create_app("testing")
    with app.app_context():
        _db.create_all()
        from app.seed.seed_plan import seed_plan, seed_sectores, seed_actores_beneficiarios
        seed_plan()
        seed_sectores()
        seed_actores_beneficiarios()
        yield app
        _db.drop_all()


@pytest.fixture(scope="function")
def db(app):
    with app.app_context():
        _db.session.begin_nested()
        yield _db
        _db.session.rollback()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def logged_in_client(client):
    with client.session_transaction() as sess:
        sess["admin"] = True
    return client
