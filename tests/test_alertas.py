"""Tests de la Fase 9: Alertas operativas (app/services/alertas_service.py)."""
import uuid

from app import db
from app.models.webhook import Webhook
from app.services.alertas_service import (
    obtener_alertas,
    _alertas_confianza_baja,
    _alertas_pico_participacion,
    _alertas_sectores_sin_politica,
    _alertas_webhooks_fallidos,
    _alertas_transcripciones_pendientes,
)


class TestServicio:

    def _limpiar_webhooks(self):
        from app.models.webhook import Webhook as _Wh
        _Wh.query.delete()
        db.session.commit()

    def test_sin_datos_no_hay_alertas(self, db):
        self._limpiar_webhooks()
        assert obtener_alertas() == []

    def test_webhook_fallido_genera_alerta(self, db):
        self._limpiar_webhooks()
        wh = Webhook(nombre="wh", url="https://x.com", evento="test", activo=True, ultimo_estado=500)
        db.session.add(wh)
        db.session.commit()
        alertas = obtener_alertas()
        assert any("webhook" in a["titulo"] for a in alertas)

    def test_webhook_ok_no_alerta(self, db):
        self._limpiar_webhooks()
        wh = Webhook(nombre="wh", url="https://x.com", evento="test", activo=True, ultimo_estado=200)
        db.session.add(wh)
        db.session.commit()
        assert _alertas_webhooks_fallidos() == []

    def test_ordenamiento_por_severidad(self, db):
        self._limpiar_webhooks()
        wh = Webhook(nombre="wh", url="https://x.com", evento="test", activo=True, ultimo_estado=500)
        db.session.add(wh)
        db.session.commit()
        alertas = obtener_alertas()
        severidades = [a["severidad"] for a in alertas]
        assert severidades == sorted(severidades, key={"alta": 0, "media": 1, "baja": 2}.get)

    def test_helpers_vacios(self, db):
        self._limpiar_webhooks()
        assert _alertas_confianza_baja() == []
        assert _alertas_pico_participacion() == []
        assert _alertas_sectores_sin_politica() == []
        assert _alertas_transcripciones_pendientes() == []


class TestEndpoint:

    def test_api_alertas_requiere_login(self, client):
        r = client.get("/admin/api/alertas")
        assert r.status_code == 302

    def test_api_alertas_con_login(self, logged_in_client):
        r = logged_in_client.get("/admin/api/alertas")
        assert r.status_code == 200
        assert isinstance(r.get_json(), list)

    def test_dashboard_muestra_alertas(self, logged_in_client):
        wh = Webhook(nombre=f"wh-{uuid.uuid4().hex[:6]}", url="https://x.com", evento="test", activo=True, ultimo_estado=500)
        db.session.add(wh)
        db.session.commit()
        r = logged_in_client.get("/admin/")
        assert r.status_code == 200
        assert "Alertas operativas" in r.data.decode()
