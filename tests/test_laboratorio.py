"""Tests del Laboratorio de Simulación (app/routes/laboratorio.py + service)."""
from app.services.laboratorio_service import estado_actual, simular


class TestPagina:

    def test_pagina_returns_200(self, client):
        r = client.get("/laboratorio")
        assert r.status_code == 200


class TestApi:

    def test_api_estado(self, client):
        r = client.get("/api/laboratorio/estado")
        assert r.status_code == 200
        data = r.get_json()
        assert "sectores" in data
        assert "indice_armonia" in data

    def test_api_simular_sin_parametros(self, client):
        r = client.post("/api/laboratorio/simular", json={})
        assert r.status_code == 200
        data = r.get_json()
        assert "sectores" in data
        assert "resumen" in data

    def test_api_simular_con_nuevo_sector(self, client):
        r = client.post("/api/laboratorio/simular", json={
            "nuevo_sector": "Deportes",
            "nuevas_participaciones": 100,
            "presupuesto_extra": 1000,
        })
        assert r.status_code == 200
        data = r.get_json()
        nombres = [s["nombre"] for s in data["sectores"]]
        assert "Deportes" in nombres


class TestServicio:

    def test_estado_actual_estructura(self, db):
        data = estado_actual()
        assert data["total_participaciones"] >= 0
        assert 0 <= data["indice_armonia"] <= 1

    def test_simular_resumen(self, db):
        data = simular({})
        resumen = data["resumen"]
        assert "cambio_armonia" in resumen
        assert resumen["total_participaciones_base"] == resumen["total_participaciones_simulado"]
