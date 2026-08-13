"""Tests de la Fase 11: Ecosistema de Integraciones (app/routes/integraciones.py)."""
import uuid

from app import db
from app.models.webhook import Webhook
from app.services.integracion_service import PARTNERS, dispatch


def _crear_webhook() -> Webhook:
    wh = Webhook(
        nombre=f"wh-{uuid.uuid4().hex[:6]}",
        url="https://ejemplo.com/hook",
        evento="participacion.nueva",
        activo=True,
    )
    db.session.add(wh)
    db.session.commit()
    return wh


class TestPagina:

    def test_pagina_returns_200(self, client):
        r = client.get("/ecosistema")
        assert r.status_code == 200


class TestApiWebhooks:

    def test_listar_requiere_login(self, client):
        r = client.get("/api/webhooks")
        assert r.status_code == 401

    def test_listar_con_login(self, logged_in_client):
        _crear_webhook()
        r = logged_in_client.get("/api/webhooks")
        assert r.status_code == 200
        assert isinstance(r.get_json(), list)

    def test_crear_requiere_campos(self, logged_in_client):
        r = logged_in_client.post("/api/webhooks", json={"nombre": "x"})
        assert r.status_code == 400

    def test_crear_webhook(self, logged_in_client):
        r = logged_in_client.post("/api/webhooks", json={
            "nombre": f"nuevo-{uuid.uuid4().hex[:6]}",
            "url": "https://ejemplo.com/hook",
            "evento": "participacion.nueva",
        })
        assert r.status_code == 201
        data = r.get_json()
        assert data["url"] == "https://ejemplo.com/hook"

    def test_eliminar_404(self, logged_in_client):
        r = logged_in_client.delete("/api/webhooks/999999")
        assert r.status_code == 404

    def test_eliminar_webhook(self, logged_in_client):
        wh = _crear_webhook()
        r = logged_in_client.delete(f"/api/webhooks/{wh.id}")
        assert r.status_code == 200
        assert Webhook.query.get(wh.id) is None


class TestServicio:

    def test_partners_definidos(self):
        assert isinstance(PARTNERS, list)
        assert len(PARTNERS) > 0

    def test_dispatch_evento_sin_webhooks(self, db):
        resultados = dispatch("participacion.nueva", {"id": 1})
        assert isinstance(resultados, list)
