"""Tests de la Fase 12: Plataforma SaaS multi-tenant (app/routes/saas.py)."""
import uuid

from app import db
from app.models.organizacion import Organizacion


def _crear_org(nombre: str = "Alcaldia Test") -> Organizacion:
    org = Organizacion(
        nombre=nombre,
        slug=Organizacion.generar_slug(nombre),
        tipo="alcaldia",
        plan="gratuito",
        email_contacto="contacto@test.co",
        color="#0f2f75",
    )
    db.session.add(org)
    db.session.commit()
    return org


class TestLanding:

    def test_landing_returns_200(self, client):
        r = client.get("/saas")
        assert r.status_code == 200

    def test_registro_returns_200(self, client):
        r = client.get("/saas/registro")
        assert r.status_code == 200


class TestOrgLanding:

    def test_org_landing_200(self, client):
        org = _crear_org()
        r = client.get(f"/saas/{org.slug}")
        assert r.status_code == 200

    def test_org_landing_muestra_nombre(self, client):
        org = _crear_org(f"Municipio {uuid.uuid4().hex[:4]}")
        r = client.get(f"/saas/{org.slug}")
        assert org.nombre.encode() in r.data

    def test_org_inactiva_404(self, client):
        org = _crear_org()
        org.activo = False
        db.session.commit()
        r = client.get(f"/saas/{org.slug}")
        assert r.status_code == 404

    def test_org_inexistente_404(self, client):
        r = client.get("/saas/slug-inexistente-xyz")
        assert r.status_code == 404


class TestApiOrganizaciones:

    def test_listar_requiere_login(self, client):
        r = client.get("/api/organizaciones")
        assert r.status_code == 401

    def test_crear_requiere_nombre(self, client):
        r = client.post("/api/organizaciones", json={"tipo": "empresa"})
        assert r.status_code == 400

    def test_crear_organizacion(self, client):
        r = client.post("/api/organizaciones", json={
            "nombre": f"Gobernacion {uuid.uuid4().hex[:4]}",
            "tipo": "gobernacion",
            "plan": "profesional",
            "email_contacto": "gob@test.co",
            "color": "#1e40af",
        })
        assert r.status_code == 201
        data = r.get_json()
        assert data["slug"]
        assert data["email_contacto"] == "gob@test.co"
        assert data["color"] == "#1e40af"

    def test_slug_unicidad(self, client):
        _crear_org("Nombre Unico Org")
        r = client.post("/api/organizaciones", json={"nombre": "Nombre Unico Org", "tipo": "empresa"})
        assert r.status_code == 201
        assert r.get_json()["slug"] != "nombre-unico-org"
