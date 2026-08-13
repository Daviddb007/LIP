"""Tests de la Fase 2: Centro de Conocimiento Público.

Cubre la página ``/conocer`` (app/routes/conocimiento.py) y el contenido
estructurado de app/services/conocimiento_service.py.
"""
from app.services.conocimiento_service import (
    CASOS_REALES,
    CICLO_POLITICA,
    GLOSARIO,
    INSTRUMENTOS,
    MODULO1,
    obtener_contenido,
)


class TestPagina:

    def test_conocer_returns_200(self, client):
        r = client.get("/conocer")
        assert r.status_code == 200

    def test_conocer_usa_plantilla_base(self, client):
        r = client.get("/conocer")
        html = r.get_data(as_text=True)
        assert "Centro de Conocimiento Público" in html
        assert "Glosario interactivo" in html

    def test_ciclo_completo_renders(self, client):
        r = client.get("/conocer")
        html = r.get_data(as_text=True)
        for paso in CICLO_POLITICA:
            assert paso["titulo"] in html
            assert paso["pregunta_clave"] in html

    def test_instrumentos_renders(self, client):
        r = client.get("/conocer")
        html = r.get_data(as_text=True)
        for item in INSTRUMENTOS:
            assert item["nombre"] in html

    def test_glosario_renders(self, client):
        r = client.get("/conocer")
        html = r.get_data(as_text=True)
        for termino in GLOSARIO:
            assert termino["termino"] in html

    def test_casos_reales_renders(self, client):
        r = client.get("/conocer")
        html = r.get_data(as_text=True)
        for caso in CASOS_REALES:
            assert caso["titulo"] in html


class TestContenido:

    def test_obtener_contenido_agrupa_todos_los_bloques(self):
        contenido = obtener_contenido()
        assert set(contenido.keys()) == {"modulo1", "ciclo", "instrumentos", "glosario", "casos"}

    def test_modulo1_tiene_caso_practico(self):
        assert MODULO1["caso_practico"]["pasos"]
        assert len(MODULO1["ingredientes"]) == 3

    def test_ciclo_tiene_8_pasos_secuenciales(self):
        assert len(CICLO_POLITICA) == 8
        assert [p["numero"] for p in CICLO_POLITICA] == list(range(1, 9))

    def test_glosario_terminos_con_relaciones(self):
        for termino in GLOSARIO:
            assert termino["termino"]
            assert termino["definicion"]
            assert isinstance(termino["relacionados"], list)

    def test_instrumentos_tienen_campos_completos(self):
        for item in INSTRUMENTOS:
            assert item["nombre"]
            assert item["jerarquia"]
            assert item["que_es"]
            assert item["ejemplo"]
            assert item["slug"]
