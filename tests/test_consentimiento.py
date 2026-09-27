"""Tests de consentimiento de datos (Ley 1581 de 2012)."""
import json
from app.models.participacion import Participacion


class TestValidateConsentimiento:

    def test_consentimiento_requerido(self, client):
        response = client.post("/api/enviar", json={
            "departamento": "Bogotá D.C.",
            "municipio": "Bogotá",
            "zona": "urbana",
            "problema_ids": [1],
            "justificacion": "Test",
            "propuesta": "Test",
            "actor_ids": [1],
            "beneficiario_ids": [1],
        })
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "autorizar" in data.get("error", "").lower() or "consent" in data.get("error", "").lower()

    def test_consentimiento_false_rechazado(self, client):
        response = client.post("/api/enviar", json={
            "consentimiento_aceptado": False,
            "departamento": "Bogotá D.C.",
            "municipio": "Bogotá",
            "zona": "urbana",
            "problema_ids": [1],
            "justificacion": "Test",
            "propuesta": "Test",
            "actor_ids": [1],
            "beneficiario_ids": [1],
        })
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "autorizar" in data.get("error", "").lower()

    def test_consentimiento_version_faltante(self, client):
        response = client.post("/api/enviar", json={
            "consentimiento_aceptado": True,
            "departamento": "Bogotá D.C.",
            "municipio": "Bogotá",
            "zona": "urbana",
            "problema_ids": [1],
            "justificacion": "Test",
            "propuesta": "Test",
            "actor_ids": [1],
            "beneficiario_ids": [1],
        })
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "versión" in data.get("error", "").lower()


class TestLegalPages:

    def test_tratamiento_datos_returns_200(self, client):
        response = client.get("/legal/tratamiento-datos")
        assert response.status_code == 200
        assert "Ley 1581" in response.data.decode()

    def test_transparencia_returns_200(self, client):
        response = client.get("/legal/transparencia")
        assert response.status_code == 200
        assert "Metodología" in response.data.decode()

    def test_terminos_returns_200(self, client):
        response = client.get("/legal/terminos")
        assert response.status_code == 200

    def test_privacidad_returns_200(self, client):
        response = client.get("/legal/privacidad")
        assert response.status_code == 200

    def test_derechos_titulares_returns_200(self, client):
        response = client.get("/legal/derechos-titulares")
        assert response.status_code == 200
        assert "ARCO" in response.data.decode()

    def test_cookies_returns_200(self, client):
        response = client.get("/legal/cookies")
        assert response.status_code == 200
        assert "Cookie" in response.data.decode() or "cookie" in response.data.decode()


class TestModeloConsentimiento:

    def test_consentimiento_fields_exist(self, app, db):
        """Verifica que el modelo tenga los campos de consentimiento."""
        cols = {c.name for c in Participacion.__table__.columns}
        assert "consentimiento_aceptado" in cols
        assert "consentimiento_version" in cols
        assert "consentimiento_at" in cols
        assert "anonimizada" in cols

    def test_consentimiento_defaults(self, app, db):
        """Crea una participacion sin consentimiento y verifica defaults."""

        p = Participacion(
            departamento="Bogotá D.C.",
            municipio="Bogotá",
            zona="urbana",
            justificacion="Test",
            propuesta="Test",
        )
        db.session.add(p)
        db.session.flush()
        assert p.consentimiento_aceptado is False
        assert p.consentimiento_version == "2026-01"
        assert p.consentimiento_at is None
        assert p.anonimizada is False


class TestAnonimizar:

    def test_to_admin_dict_includes_consent(self, app, db):

        p = Participacion(
            departamento="Antioquia",
            municipio="Medellín",
            zona="urbana",
            justificacion="Test anonimizar",
            propuesta="Test",
        )
        db.session.add(p)
        db.session.flush()

        ad = p.to_admin_dict()
        assert "consentimiento_aceptado" in ad
        assert "consentimiento_version" in ad
        assert "anonimizada" in ad

    def test_to_dict_public_excludes_consent(self, app, db):

        p = Participacion(
            departamento="Cundinamarca",
            municipio="Soacha",
            zona="urbana",
            justificacion="Test público",
            propuesta="Test",
        )
        db.session.add(p)
        db.session.flush()

        d = p.to_dict()
        assert "consentimiento_aceptado" not in d
        assert "consentimiento_version" not in d
        assert "anonimizada" not in d
