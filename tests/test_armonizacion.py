"""Tests de Armonización Estratégica (app/services/armonizacion_service.py)."""
from app.services.armonizacion_service import generar_armonizacion


class TestPagina:

    def test_pagina_returns_200(self, client):
        r = client.get("/armonizacion")
        assert r.status_code == 200


class TestApi:

    def test_api_armonizacion_returns_200(self, client):
        r = client.get("/api/armonizacion")
        assert r.status_code == 200

    def test_api_armonizacion_has_claves_esenciales(self, client):
        data = client.get("/api/armonizacion").get_json()
        assert "matriz" in data
        assert "gaps" in data
        assert "coincidencias" in data or "resumen" in data or "oportunidades" in data


class TestServicio:

    def test_generar_armonizacion_estructura(self, db):
        data = generar_armonizacion()
        assert "matriz" in data
        assert "gaps" in data
        assert isinstance(data["matriz"], list)

    def test_nivel_es_valido(self, db):
        niveles = {"alto", "medio", "bajo"}
        data = generar_armonizacion()
        for fila in data["matriz"]:
            assert "nivel_prioridad" in fila
            assert fila["nivel_prioridad"] in niveles
            assert "nivel_cobertura" in fila
            assert fila["nivel_cobertura"] in niveles
