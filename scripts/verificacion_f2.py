"""Verificación end-to-end F2: Centro de Conocimiento Público.

Ejercita la página ``/conocer`` y valida el contrato del contenido
estructurado que alimenta los 5 módulos educativos.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.services.conocimiento_service import (
    CASOS_REALES,
    CICLO_POLITICA,
    GLOSARIO,
    INSTRUMENTOS,
    MODULO1,
    obtener_contenido,
)

app = create_app("testing")

with app.test_client() as c:
    r = c.get("/conocer")
    assert r.status_code == 200, r.status_code
    html = r.get_data(as_text=True)

    assert "Centro de Conocimiento Público" in html
    assert len(CICLO_POLITICA) == 8, "el ciclo debe tener 8 etapas"
    for paso in CICLO_POLITICA:
        assert paso["titulo"] in html, f"falta etapa del ciclo: {paso['titulo']}"
        assert paso["pregunta_clave"] in html, f"falta pregunta de {paso['titulo']}"

    for item in INSTRUMENTOS:
        assert item["nombre"] in html, f"falta instrumento: {item['nombre']}"
        assert f'instrumento{item["slug"]}' in html, f"falta modal de {item['nombre']}"

    for termino in GLOSARIO:
        assert termino["termino"] in html, f"falta término del glosario: {termino['termino']}"
        assert termino["definicion"] in html, f"falta definición de {termino['termino']}"

    for caso in CASOS_REALES:
        assert caso["titulo"] in html, f"falta caso real: {caso['titulo']}"

    assert MODULO1["titulo"] in html
    assert MODULO1["caso_practico"]["titulo"] in html

contenido = obtener_contenido()
assert set(contenido.keys()) == {"modulo1", "ciclo", "instrumentos", "glosario", "casos"}

print(f"F2 E2E OK: /conocer con {len(MODULO1['ingredientes'])} ingredientes, "
      f"{len(CICLO_POLITICA)} etapas, {len(INSTRUMENTOS)} instrumentos, "
      f"{len(GLOSARIO)} términos y {len(CASOS_REALES)} casos reales")
