"""Tests de la Fase 3: Biblioteca Inteligente (app/routes/biblioteca.py)."""
import uuid

import pytest

from app import db
from app.models.catalog import Sector
from app.models.politica import Politica


def _crear_politica() -> Politica:
    sector = Sector.query.filter_by(activo=True).first()
    politica = Politica(
        titulo=f"Política test {uuid.uuid4().hex[:8]}",
        sector_id=sector.id if sector else None,
        resumen_ejecutivo="Resumen de prueba para la biblioteca.",
        problema="Problema de prueba.",
        estado="Activa",
        activo=True,
    )
    db.session.add(politica)
    db.session.commit()
    return politica


class TestPagina:

    def test_lista_returns_200(self, client):
        r = client.get("/biblioteca")
        assert r.status_code == 200

    def test_lista_con_filtro_estado(self, client):
        _crear_politica()
        r = client.get("/biblioteca?estado=Activa")
        assert r.status_code == 200

    def test_lista_con_filtro_sector_invalido(self, client):
        r = client.get("/biblioteca?sector=no-numero")
        assert r.status_code == 200

    def test_detalle_404_para_inexistente(self, client):
        r = client.get("/biblioteca/999999")
        assert r.status_code == 404


class TestApi:

    def test_api_lista_returns_json(self, client):
        _crear_politica()
        r = client.get("/api/politicas")
        assert r.status_code == 200
        data = r.get_json()
        assert isinstance(data, list)
        assert all("titulo" in p for p in data)

    def test_api_detalle(self, client):
        politica = _crear_politica()
        r = client.get(f"/api/politicas/{politica.id}")
        assert r.status_code == 200
        assert r.get_json()["titulo"] == politica.titulo

    def test_api_detalle_404(self, client):
        r = client.get("/api/politicas/999999")
        assert r.status_code == 404

    def test_preguntar_requiere_pregunta(self, client):
        politica = _crear_politica()
        r = client.post(f"/api/politicas/{politica.id}/preguntar", json={})
        assert r.status_code == 400

    def test_preguntar_responde(self, client):
        politica = _crear_politica()
        r = client.post(
            f"/api/politicas/{politica.id}/preguntar",
            json={"pregunta": "agua potable para todos"},
        )
        assert r.status_code == 200
        data = r.get_json()
        assert data["politica_id"] == politica.id
        assert data["respuesta"]

    def test_preguntar_politica_404(self, client):
        r = client.post("/api/politicas/999999/preguntar", json={"pregunta": "x"})
        assert r.status_code == 404
