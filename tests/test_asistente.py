"""Tests de la Fase 6: Asistente Público SRIE (app/routes/asistente.py)."""
from app.services.asistente_service import normalizar, responder


class TestPagina:

    def test_pagina_returns_200(self, client):
        r = client.get("/asistente")
        assert r.status_code == 200


class TestApi:

    def test_preguntar_requiere_pregunta(self, client):
        r = client.post("/api/asistente/preguntar", json={})
        assert r.status_code == 400

    def test_preguntar_pregunta_vacia(self, client):
        r = client.post("/api/asistente/preguntar", json={"pregunta": "   "})
        assert r.status_code == 400

    def test_preguntar_conoce_entidades(self, client):
        r = client.post("/api/asistente/preguntar", json={"pregunta": "que hace el congreso?"})
        assert r.status_code == 200
        data = r.get_json()
        assert data["tiene_respuesta"] is True
        assert data["respuesta"]

    def test_preguntar_desconocido(self, client):
        r = client.post("/api/asistente/preguntar", json={"pregunta": "zzz qqq xxx yyy"})
        assert r.status_code == 200
        assert r.get_json()["tiene_respuesta"] is False


class TestServicio:

    def test_normalizar_quita_tildes(self):
        assert normalizar("¿QUÉ ES EL CONGRESO?") == "que es el congreso?"

    def test_responder_pnd(self):
        data = responder("¿qué es el plan nacional de desarrollo?")
        assert data["tiene_respuesta"] is True
        assert "PND" in data["respuesta"] or "Plan Nacional de Desarrollo" in data["respuesta"]
