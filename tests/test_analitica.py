"""Tests del módulo de Analítica Avanzada (Fase 8).

Los tests usan textos con prefijo "analitica_test" y limpian las
participaciones creadas al final de cada test (el fixture `db` commitea).
"""
from __future__ import annotations

from datetime import datetime

import pytest

from app.models.participacion import Participacion
from app.services import analitica_service as s


def _crear_participacion(db, texto, depto="Antioquia", municipio="Medellín", mes=1, dia=1):
    p = Participacion(
        departamento=depto,
        municipio=municipio,
        zona="urbana",
        justificacion="contexto de prueba",
        propuesta=texto,
        consentimiento_aceptado=True,
        consentimiento_version="2026-01",
        consentimiento_at=datetime(2026, 1, 1),
    )
    p.created_at = datetime(2026, mes, dia)
    db.session.add(p)
    db.session.flush()
    return p


def _limpiar(db):
    db.session.query(Participacion).delete()
    db.session.commit()


def test_obtener_analitica_estructura_completa(db):
    _crear_participacion(db, "analitica_test carretera puente vía transporte")
    try:
        data = s.obtener_analitica()
        assert set(data) >= {
            "nube_palabras", "clusters", "tendencias",
            "territorio", "comparativas", "predicciones", "resumen",
        }
        assert data["resumen"]["total_clusters"] >= 0
        assert isinstance(data["nube_palabras"], list)
    finally:
        _limpiar(db)


def test_extraer_palabras_filtra_stopwords_y_cortas(db):
    _crear_participacion(db, "de la que en una el camino vecinal conecta")
    try:
        palabras = s._extraer_palabras()
        textos = [p["texto"] for p in palabras]
        assert "camino" in textos
        assert "vecinal" in textos
        assert "conecta" in textos
        assert "de" not in textos
        assert "que" not in textos
    finally:
        _limpiar(db)


def test_clusters_semanticos_asignan_por_similitud(db):
    _crear_participacion(db, "analitica_test falta una carretera nueva y un puente para mejorar la vía")
    _crear_participacion(db, "analitica_test la escuela del colegio necesita docentes y becas para los estudiantes")
    try:
        asignacion, textos = s._asignacion_semantica()
        clusters = s._clusters_desde(asignacion, textos)
        nombres = {c["nombre"]: c["participaciones"] for c in clusters}
        assert nombres.get("Infraestructura", 0) >= 1
        assert nombres.get("Educación", 0) >= 1
        for c in clusters:
            assert c["participaciones"] >= 1
            assert isinstance(c["palabras_clave"], list)
    finally:
        _limpiar(db)


def test_clusters_semanticos_sin_datos(db):
    asignacion, textos = s._asignacion_semantica()
    assert asignacion == {}
    assert s._clusters_desde(asignacion, textos) == []


def test_centroide_cluster_normalizado(db):
    import math

    centro = s._centroide_cluster("Salud")
    assert centro
    norma = math.sqrt(sum(x * x for x in centro))
    assert abs(norma - 1.0) < 1e-6


def test_tendencia_mensual_con_tema_dominante(db):
    _crear_participacion(db, "analitica_test carretera puente vía", depto="Antioquia", mes=8)
    _crear_participacion(db, "analitica_test escuela colegio educación", depto="Cundinamarca", mes=9)
    try:
        asignacion, _ = s._asignacion_semantica()
        tendencias = s._tendencia_mensual(asignacion)
        assert len(tendencias) == 2
        for t in tendencias:
            assert "tema_dominante" in t
            assert "participacion_tema" in t
            assert t["participaciones"] == 1
    finally:
        _limpiar(db)


def test_tendencia_mensual_sin_asignacion(db):
    _crear_participacion(db, "analitica_test algo", mes=8)
    try:
        tendencias = s._tendencia_mensual()
        assert tendencias[0]["mes"] == "2026-08"
        assert tendencias[0]["participaciones"] == 1
        assert "tema_dominante" not in tendencias[0]
    finally:
        _limpiar(db)


def test_analisis_territorial_por_region(db):
    _crear_participacion(db, "analitica_test carretera", depto="Antioquia", municipio="Medellín")
    try:
        territorio = s._analisis_territorial()
        andina = next((t for t in territorio if t["region"] == "Andina"), None)
        assert andina is not None
        assert andina["total"] >= 1
        assert any(d["nombre"] == "Antioquia" for d in andina["departamentos"])
    finally:
        _limpiar(db)


def test_predicciones_creciente(db):
    _crear_participacion(db, "analitica_test a", mes=8)
    _crear_participacion(db, "analitica_test b", mes=9)
    _crear_participacion(db, "analitica_test c", mes=9)
    _crear_participacion(db, "analitica_test d", mes=10)
    _crear_participacion(db, "analitica_test e", mes=10)
    _crear_participacion(db, "analitica_test f", mes=10)
    try:
        prediccion = s._predicciones()
        assert prediccion["proyeccion_tendencia"] == "creciente"
        assert prediccion["estimado_proximo_mes"] >= 2
    finally:
        _limpiar(db)


def test_comparativas_sector_estructura(db):
    _crear_participacion(db, "analitica_test carretera")
    try:
        comparativas = s._comparativas_sector()
        assert set(comparativas) >= {
            "sector_lider", "departamento_lider", "total_sectores",
            "sectores_sin_politica", "sectores",
        }
        assert "nombre" in comparativas["sector_lider"]
        assert isinstance(comparativas["sectores"], list)
    finally:
        _limpiar(db)


def test_api_analitica_retorna_json(client, db):
    _crear_participacion(db, "analitica_test carretera puente")
    try:
        r = client.get("/api/analitica")
        assert r.status_code == 200
        assert r.is_json
        assert "clusters" in r.get_json()
    finally:
        _limpiar(db)


def test_api_v1_analitica_retorna_json(client, db):
    _crear_participacion(db, "analitica_test carretera puente")
    try:
        r = client.get("/api/v1/analitica")
        assert r.status_code == 200
        assert r.is_json
        assert "nube_palabras" in r.get_json()
    finally:
        _limpiar(db)
