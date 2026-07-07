"""Tests de integración para endpoints API y rutas públicas v2."""
import json

import pytest

from app import db
from app.models.participacion import Participacion, ClasificacionSRIE
from app.models.plan import Plan, Pilar
from app.models.catalog import ProblemaCatalogo, Actor, Beneficiario


class TestHealthCheck:

    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "healthy"

    def test_health_returns_json(self, client):
        response = client.get("/health")
        assert response.content_type == "application/json"


class TestHome:

    def test_home_returns_200(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_home_contains_title(self, client):
        response = client.get("/")
        assert "Laboratorio de Inteligencia Pública" in response.data.decode()


class TestIniciativa:

    def test_iniciativa_returns_200(self, client):
        response = client.get("/iniciativa")
        assert response.status_code == 200

    def test_iniciativa_contains_srie(self, client):
        response = client.get("/iniciativa")
        assert "SRIE" in response.data.decode() or "Reconocimiento" in response.data.decode()


class TestParticipar:

    def test_participar_returns_200(self, client):
        response = client.get("/participar")
        assert response.status_code == 200

    def test_participar_contains_form(self, client):
        response = client.get("/participar")
        assert "form" in response.data.decode().lower() or "step" in response.data.decode().lower()


class TestResultados:

    def test_resultados_returns_200(self, client):
        response = client.get("/resultados")
        assert response.status_code == 200

    def test_resultados_contains_stats(self, client):
        response = client.get("/resultados")
        assert "Resultados" in response.data.decode() or "resultados" in response.data.decode()


class TestApiCatalogoSectores:

    def test_api_sectores_returns_200(self, client):
        response = client.get("/api/catalogo/sectores")
        assert response.status_code == 200

    def test_api_sectores_returns_json(self, client):
        response = client.get("/api/catalogo/sectores")
        assert response.content_type == "application/json"

    def test_api_sectores_returns_list(self, client):
        response = client.get("/api/catalogo/sectores")
        data = json.loads(response.data)
        assert isinstance(data, list)


class TestApiCatalogoActores:

    def test_api_actores_returns_200(self, client):
        response = client.get("/api/catalogo/actores")
        assert response.status_code == 200

    def test_api_actores_returns_json(self, client):
        response = client.get("/api/catalogo/actores")
        assert response.content_type == "application/json"


class TestApiCatalogoBeneficiarios:

    def test_api_beneficiarios_returns_200(self, client):
        response = client.get("/api/catalogo/beneficiarios")
        assert response.status_code == 200

    def test_api_beneficiarios_returns_json(self, client):
        response = client.get("/api/catalogo/beneficiarios")
        assert response.content_type == "application/json"


class TestApiEstadisticas:

    def test_api_estadisticas_returns_200(self, client):
        response = client.get("/api/estadisticas")
        assert response.status_code == 200

    def test_api_estadisticas_returns_json(self, client):
        response = client.get("/api/estadisticas")
        assert response.content_type == "application/json"

    def test_api_estadisticas_has_keys(self, client):
        response = client.get("/api/estadisticas")
        data = json.loads(response.data)
        assert "total" in data
        assert "departamentos" in data
        assert "actores" in data
        assert "beneficiarios" in data


class TestApiParticipaciones:

    def test_api_participaciones_returns_200(self, client):
        response = client.get("/api/participaciones")
        assert response.status_code == 200

    def test_api_participaciones_returns_json(self, client):
        response = client.get("/api/participaciones")
        assert response.content_type == "application/json"


class TestApiEnviar:

    def test_api_enviar_requires_json(self, client):
        response = client.post("/api/enviar", content_type="text/html")
        assert response.status_code == 400

    def test_api_enviar_requires_data(self, client):
        response = client.post("/api/enviar", json={})
        assert response.status_code == 400

    def test_api_enviar_validates_departamento(self, client):
        data = {
            "municipio": "Bogotá",
            "zona": "urbana",
            "problema_ids": [1],
            "justificacion": "Test justificación",
            "propuesta": "Test propuesta",
            "actor_ids": [1],
            "beneficiario_ids": [1],
        }
        response = client.post("/api/enviar", json=data)
        assert response.status_code == 400

    def test_api_enviar_validates_municipio(self, client):
        data = {
            "departamento": "Bogotá D.C.",
            "municipio": "",
            "zona": "urbana",
            "problema_ids": [1],
            "justificacion": "Test justificación",
            "propuesta": "Test propuesta",
            "actor_ids": [1],
            "beneficiario_ids": [1],
        }
        response = client.post("/api/enviar", json=data)
        assert response.status_code == 400

    def test_api_enviar_validates_zona(self, client):
        data = {
            "departamento": "Bogotá D.C.",
            "municipio": "Bogotá",
            "zona": "costera",
            "problema_ids": [1],
            "justificacion": "Test justificación",
            "propuesta": "Test propuesta",
            "actor_ids": [1],
            "beneficiario_ids": [1],
        }
        response = client.post("/api/enviar", json=data)
        assert response.status_code == 400

    def test_api_enviar_validates_textos(self, client):
        data = {
            "departamento": "Bogotá D.C.",
            "municipio": "Bogotá",
            "zona": "urbana",
            "problema_ids": [1],
            "justificacion": "",
            "propuesta": "Test propuesta",
            "actor_ids": [1],
            "beneficiario_ids": [1],
        }
        response = client.post("/api/enviar", json=data)
        assert response.status_code == 400

    def test_api_enviar_validates_problemas(self, client):
        data = {
            "departamento": "Bogotá D.C.",
            "municipio": "Bogotá",
            "zona": "urbana",
            "problema_ids": [],
            "justificacion": "Test justificación",
            "propuesta": "Test propuesta",
            "actor_ids": [1],
            "beneficiario_ids": [1],
        }
        response = client.post("/api/enviar", json=data)
        assert response.status_code == 400


class TestAdmin:

    def test_admin_login_returns_200(self, client):
        response = client.get("/admin/login")
        assert response.status_code == 200

    def test_admin_dashboard_requires_login(self, client):
        response = client.get("/admin/")
        assert response.status_code == 302

    def test_admin_dashboard_with_session(self, logged_in_client):
        response = logged_in_client.get("/admin/")
        assert response.status_code == 200

    def test_admin_participaciones_requires_login(self, client):
        response = client.get("/admin/participaciones")
        assert response.status_code == 302

    def test_admin_participaciones_with_session(self, logged_in_client):
        response = logged_in_client.get("/admin/participaciones")
        assert response.status_code == 200

    def test_admin_sectores_requires_login(self, client):
        response = client.get("/admin/sectores")
        assert response.status_code == 302

    def test_admin_sectores_with_session(self, logged_in_client):
        response = logged_in_client.get("/admin/sectores")
        assert response.status_code == 200

    def test_admin_pilares_requires_login(self, client):
        response = client.get("/admin/pilares")
        assert response.status_code == 302

    def test_admin_pilares_with_session(self, logged_in_client):
        response = logged_in_client.get("/admin/pilares")
        assert response.status_code == 200

    def test_admin_problemas_requires_login(self, client):
        response = client.get("/admin/problemas")
        assert response.status_code == 302

    def test_admin_problemas_with_session(self, logged_in_client):
        response = logged_in_client.get("/admin/problemas")
        assert response.status_code == 200

    def test_admin_actores_requires_login(self, client):
        response = client.get("/admin/actores")
        assert response.status_code == 302

    def test_admin_actores_with_session(self, logged_in_client):
        response = logged_in_client.get("/admin/actores")
        assert response.status_code == 200

    def test_admin_beneficiarios_requires_login(self, client):
        response = client.get("/admin/beneficiarios")
        assert response.status_code == 302

    def test_admin_beneficiarios_with_session(self, logged_in_client):
        response = logged_in_client.get("/admin/beneficiarios")
        assert response.status_code == 200

    def test_admin_clasificaciones_requires_login(self, client):
        response = client.get("/admin/clasificaciones")
        assert response.status_code == 302

    def test_admin_clasificaciones_with_session(self, logged_in_client):
        response = logged_in_client.get("/admin/clasificaciones")
        assert response.status_code == 200

    def test_admin_planes_requires_login(self, client):
        response = client.get("/admin/planes")
        assert response.status_code == 302

    def test_admin_planes_with_session(self, logged_in_client):
        response = logged_in_client.get("/admin/planes")
        assert response.status_code == 200

    def test_admin_export_requires_login(self, client):
        response = client.get("/admin/export")
        assert response.status_code == 302

    def test_admin_export_with_session(self, logged_in_client):
        response = logged_in_client.get("/admin/export")
        assert response.status_code == 200

    def test_admin_config_requires_login(self, client):
        response = client.get("/admin/config")
        assert response.status_code == 302

    def test_admin_config_with_session(self, logged_in_client):
        response = logged_in_client.get("/admin/config")
        assert response.status_code == 200

    def test_admin_logs_requires_login(self, client):
        response = client.get("/admin/logs")
        assert response.status_code == 302

    def test_admin_logs_with_session(self, logged_in_client):
        response = logged_in_client.get("/admin/logs")
        assert response.status_code == 200

    def test_admin_logout(self, logged_in_client):
        response = logged_in_client.get("/admin/logout", follow_redirects=True)
        assert response.status_code == 200
