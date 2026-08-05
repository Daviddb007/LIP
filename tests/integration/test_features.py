"""Tests de integración para nuevas rutas portadas de V2 a V3."""
import json

import pytest

from app import db
from app.models.politica import Politica
from app.models.miembro import MiembroEquipo
from app.models.organizacion import Organizacion
from app.models.webhook import Webhook
from app.models.api_token import ApiToken


class TestBiblioteca:

    def test_biblioteca_returns_200(self, client):
        response = client.get("/biblioteca")
        assert response.status_code == 200

    def test_api_politicas_returns_200(self, client):
        response = client.get("/api/politicas")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list) or "data" in data

    def test_biblioteca_detalle_404(self, client):
        response = client.get("/biblioteca/999")
        assert response.status_code == 404


class TestAsistente:

    def test_asistente_returns_200(self, client):
        response = client.get("/asistente")
        assert response.status_code == 200

    def test_api_asistente_preguntar_requires_json(self, client):
        response = client.post("/api/asistente/preguntar")
        assert response.status_code == 400

    def test_api_asistente_preguntar_requires_pregunta(self, client):
        response = client.post("/api/asistente/preguntar", json={})
        assert response.status_code == 400

    def test_api_asistente_responde(self, client):
        response = client.post("/api/asistente/preguntar", json={"pregunta": "¿qué es el PND?"})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "tiene_respuesta" in data

    def test_api_asistente_sin_respuesta(self, client):
        response = client.post("/api/asistente/preguntar", json={"pregunta": "xyz123notfound"})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["tiene_respuesta"] is False


class TestArmonizacion:

    def test_armonizacion_returns_200(self, client):
        response = client.get("/armonizacion")
        assert response.status_code == 200

    def test_api_armonizacion_returns_json(self, client):
        response = client.get("/api/armonizacion")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "resumen" in data
        assert "matriz" in data


class TestLaboratorio:

    def test_laboratorio_returns_200(self, client):
        response = client.get("/laboratorio")
        assert response.status_code == 200

    def test_api_laboratorio_estado(self, client):
        response = client.get("/api/laboratorio/estado")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "sectores" in data
        assert "indice_armonia" in data

    def test_api_laboratorio_simular(self, client):
        response = client.post("/api/laboratorio/simular", json={"presupuesto_extra": 1000})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "resumen" in data
        assert "sectores" in data


class TestAnalitica:

    def test_analitica_returns_200(self, client):
        response = client.get("/analitica")
        assert response.status_code == 200

    def test_api_analitica_returns_json(self, client):
        response = client.get("/api/analitica")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "nube_palabras" in data
        assert "clusters" in data


class TestIntegraciones:

    def test_ecosistema_returns_200(self, client):
        response = client.get("/ecosistema")
        assert response.status_code == 200

    def test_api_webhooks_requires_login(self, client):
        response = client.get("/api/webhooks")
        assert response.status_code == 401

    def test_api_webhooks_with_session(self, logged_in_client):
        response = logged_in_client.get("/api/webhooks")
        assert response.status_code == 200

    def test_api_webhooks_crear(self, logged_in_client):
        response = logged_in_client.post("/api/webhooks", json={
            "nombre": "Test", "url": "https://example.com/hook", "evento": "participacion.nueva",
        })
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["nombre"] == "Test"

    def test_api_webhooks_eliminar(self, logged_in_client):
        wh = Webhook(nombre="Del", url="https://del.com", evento="test")
        db.session.add(wh)
        db.session.commit()

        response = logged_in_client.delete(f"/api/webhooks/{wh.id}")
        assert response.status_code == 200


class TestSaaS:

    def test_saas_returns_200(self, client):
        response = client.get("/saas")
        assert response.status_code == 200

    def test_api_organizaciones_crear(self, client):
        response = client.post("/api/organizaciones", json={"nombre": "Test Org", "tipo": "universidad"})
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["nombre"] == "Test Org"
        assert data["slug"] == "test-org"

    def test_api_organizaciones_listar_requires_login(self, client):
        response = client.get("/api/organizaciones")
        assert response.status_code == 401

    def test_api_organizaciones_listar_with_session(self, logged_in_client):
        response = logged_in_client.get("/api/organizaciones")
        assert response.status_code == 200


class TestNosotros:

    def test_nosotros_returns_200(self, client):
        response = client.get("/nosotros")
        assert response.status_code == 200


class TestApiV1:

    def test_api_v1_root(self, client):
        response = client.get("/api/v1/")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["version"] == "1.0.0"

    def test_api_v1_estadisticas(self, client):
        response = client.get("/api/v1/estadisticas")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "total_participaciones" in data

    def test_api_v1_sectores(self, client):
        response = client.get("/api/v1/sectores")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "data" in data
        assert len(data["data"]) > 0

    def test_api_v1_politicas(self, client):
        response = client.get("/api/v1/politicas")
        assert response.status_code == 200

    def test_api_v1_participaciones_requires_auth(self, client):
        response = client.get("/api/v1/participaciones")
        assert response.status_code == 401

    def test_api_v1_token_requires_admin_token(self, client):
        response = client.post("/api/v1/token", json={"nombre": "test"})
        assert response.status_code == 403

    def test_api_v1_clasificar_requires_json(self, client):
        response = client.post("/api/v1/clasificar")
        assert response.status_code == 400

    def test_api_v1_armonizacion(self, client):
        response = client.get("/api/v1/armonizacion")
        assert response.status_code == 200

    def test_api_v1_analitica(self, client):
        response = client.get("/api/v1/analitica")
        assert response.status_code == 200
