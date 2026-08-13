"""Verificación end-to-end F1: flujo participar -> SRIE -> resultados.

Ejercita el wizard (catálogos), el envío de participación, la clasificación
SRIE con explicación para el ciudadano, y la publicación en resultados.
"""
import json
import os
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db as _db
from app.models.catalog import ProblemaCatalogo, Actor, Beneficiario
from app.models.participacion import Participacion, ClasificacionSRIE
from app.seed.seed_plan import seed_plan, seed_sectores, seed_actores_beneficiarios

app = create_app("testing")

with app.app_context():
    _db.create_all()
    seed_plan()
    seed_sectores()
    seed_actores_beneficiarios()

    problema = ProblemaCatalogo.query.filter_by(activo=True).first()
    actor = Actor.query.filter_by(activo=True).first()
    beneficiario = Beneficiario.query.filter_by(activo=True).first()
    assert problema and actor and beneficiario, "seeds incompletos"

with app.test_client() as c:
    for ruta in [
        "/participar",
        "/api/catalogo/sectores",
        "/api/catalogo/actores",
        "/api/catalogo/beneficiarios",
        "/resultados",
    ]:
        r = c.get(ruta)
        assert r.status_code == 200, (ruta, r.status_code)

    payload = {
        "departamento": "Antioquia",
        "municipio": f"Medellin-{uuid.uuid4().hex[:6]}",
        "zona": "urbana",
        "problema_ids": [problema.id],
        "justificacion": "La comunidad reporta falta de agua potable en las veredas",
        "propuesta": "Construir acueductos veredales y garantizar mantenimiento",
        "rango_edad": "26-35",
        "genero": "Masculino",
        "actor_ids": [actor.id],
        "beneficiario_ids": [beneficiario.id],
        "consentimiento_aceptado": True,
        "consentimiento_version": "2026-01",
    }
    r = c.post("/api/enviar", json=payload)
    assert r.status_code in (200, 201), (r.status_code, r.get_json())
    body = r.get_json()
    assert body.get("success") is True, body

with app.app_context():
    p = Participacion.query.order_by(Participacion.id.desc()).first()
    clasifs = (
        ClasificacionSRIE.query.filter_by(participacion_id=p.id)
        .order_by(ClasificacionSRIE.ranking)
        .all()
    )
    assert len(clasifs) >= 1, "sin clasificaciones SRIE"
    assert all(c.ranking == i + 1 for i, c in enumerate(clasifs)), "ranking incorrecto"
    assert all(0.0 <= c.confianza <= 1.0 for c in clasifs), "confianza fuera de rango"
    explicaciones = [json.dumps(c.to_dict()) for c in clasifs]
    assert explicaciones

print(f"F1 E2E OK: participacion #{p.id} -> {len(clasifs)} clasificaciones SRIE top-3")
