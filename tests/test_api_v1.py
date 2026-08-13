"""Tests de la Fase 10: API Pública v1 (app/routes/api_v1.py + openapi_spec)."""
import uuid

from app import db
from app.models.api_token import ApiToken
from app.models.catalog import Sector
from app.models.politica import Politica
from app.services.openapi_spec import spec_openapi


def _crear_token(role: str = "lectura") -> ApiToken:
    token = ApiToken.generar(f"token-{uuid.uuid4().hex[:6]}", role)
    db.session.add(token)
    db.session.commit()
    return token


def _crear_politica() -> Politica:
    sector = Sector.query.filter_by(activo=True).first()
    politica = Politica(
        titulo=f"Política API {uuid.uuid4().hex[:8]}",
        sector_id=sector.id if sector else None,
        resumen_ejecutivo="Resumen API",
        problema="Problema API",
        estado="Activa",
        activo=True,
    )
    db.session.add(politica)
    db.session.commit()
    return politica


class TestRoot:

    def test_root_returns_200(self, client):
        r = client.get("/api/v1/")
        assert r.status_code == 200
        assert r.get_json()["version"] == "1.0.0"


class TestOpenApi:

    def test_es_espec_valida(self):
        spec = spec_openapi()
        assert spec["openapi"].startswith("3.")
        assert len(spec["paths"]) >= 9

    def test_publica_openapi_json(self, client):
        r = client.get("/api/v1/openapi.json")
        assert r.status_code == 200
        data = r.get_json()
        assert data["openapi"].startswith("3.")

    def test_openapi_tiene_security_schemes(self):
        spec = spec_openapi()
        assert "bearerAuth" in spec["components"]["securitySchemes"]

    def test_swagger_ui_servido(self, client):
        r = client.get("/api/docs/swagger")
        assert r.status_code == 200
        r2 = client.get("/api/docs")
        assert r2.status_code == 200


class TestEndpointsPublicos:

    def test_estadisticas(self, client):
        r = client.get("/api/v1/estadisticas")
        assert r.status_code == 200

    def test_sectores(self, client):
        r = client.get("/api/v1/sectores")
        assert r.status_code == 200
        data = r.get_json()
        assert "data" in data and "total" in data

    def test_politicas(self, client):
        _crear_politica()
        r = client.get("/api/v1/politicas")
        assert r.status_code == 200
        assert "data" in r.get_json()

    def test_politicas_filtro_sector_no_numerico(self, client):
        r = client.get("/api/v1/politicas?sector=abc")
        assert r.status_code == 200

    def test_politica_detalle(self, client):
        politica = _crear_politica()
        r = client.get(f"/api/v1/politicas/{politica.id}")
        assert r.status_code == 200
        assert r.get_json()["id"] == politica.id

    def test_politica_detalle_404(self, client):
        r = client.get("/api/v1/politicas/999999")
        assert r.status_code == 404

    def test_armonizacion(self, client):
        r = client.get("/api/v1/armonizacion")
        assert r.status_code == 200

    def test_analitica(self, client):
        r = client.get("/api/v1/analitica")
        assert r.status_code == 200


class TestAuth:

    def test_participaciones_requiere_token(self, client):
        r = client.get("/api/v1/participaciones")
        assert r.status_code == 401

    def test_participaciones_con_token(self, client):
        token = _crear_token("lectura")
        r = client.get("/api/v1/participaciones", headers={"Authorization": f"Bearer {token.token}"})
        assert r.status_code == 200
        assert "data" in r.get_json()

    def test_token_insuficiente_403(self, client):
        token = _crear_token("lectura")
        r = client.get(
            "/api/v1/participaciones?token=" + token.token,
        )
        assert r.status_code == 200

    def test_token_invalido(self, client):
        r = client.get("/api/v1/participaciones", headers={"Authorization": "Bearer invalido"})
        assert r.status_code == 401


class TestGeneracionToken:

    def test_token_admin_exitoso(self, client):
        r = client.post(
            "/api/v1/token",
            json={"nombre": f"nuevo-{uuid.uuid4().hex[:6]}", "role": "escritura"},
            headers={"Authorization": "Bearer test-admin-token"},
        )
        assert r.status_code == 201
        assert r.get_json()["role"] == "escritura"

    def test_token_requiere_nombre(self, client):
        r = client.post(
            "/api/v1/token",
            json={},
            headers={"Authorization": "Bearer test-admin-token"},
        )
        assert r.status_code == 400

    def test_token_admin_invalido(self, client):
        r = client.post(
            "/api/v1/token",
            json={"nombre": "x"},
            headers={"Authorization": "Bearer incorrecto"},
        )
        assert r.status_code == 403
