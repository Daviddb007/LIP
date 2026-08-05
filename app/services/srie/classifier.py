"""
Orquestador principal del motor SRIE v2.

Coordina matching multi-pilar, cálculo de confianza y generación de top-3 clasificaciones.
"""
from __future__ import annotations

import json

from app import db
from app.models.participacion import ClasificacionSRIE
from app.services.srie.matcher import clasificar_texto, get_pilar_by_slug
from app.services.srie.confidence import calcular_confianza
from app.services.srie.explanation import generar_explicacion


def clasificar_participacion(participacion, plan_id: int = 1):
    """Clasifica una participación contra el plan estratégico activo.

    Retorna lista de ClasificacionSRIE (top-3) y lista de explicaciones.
    """
    # Combinar textos para el matching
    texto_completo = f"{participacion.justificacion} {participacion.propuesta}"

    # Obtener problema_slug de la participación (M:N)
    from app.models.catalog import participacion_problemas, ProblemaCatalogo
    problemas = ProblemaCatalogo.query.join(
        participacion_problemas,
        participacion_problemas.c.problema_id == ProblemaCatalogo.id,
    ).filter(participacion_problemas.c.participacion_id == participacion.id).all()

    problema_slug = problemas[0].slug if problemas else None

    # Clasificar texto
    resultados = clasificar_texto(
        texto=texto_completo,
        problema_slug=problema_slug,
        top_n=3,
    )

    clasificaciones = []
    explicaciones = []

    for i, resultado in enumerate(resultados):
        pilar = get_pilar_by_slug(resultado["pilar_slug"])
        if not pilar:
            continue

        tiene_problema_directo = problema_slug is not None

        confianza = calcular_confianza(
            score=resultado["score"],
            justificacion=participacion.justificacion,
            propuesta=participacion.propuesta,
            keywords_encontradas=resultado["keywords"],
            tiene_problema_directo=tiene_problema_directo,
        )

        explicacion = generar_explicacion(
            pilar_nombre=pilar.nombre,
            confianza=confianza,
            keywords=resultado["keywords"],
            ranking=i + 1,
        )

        clasificacion = ClasificacionSRIE(
            participacion_id=participacion.id,
            pilar_id=pilar.id,
            confianza=confianza,
            ranking=i + 1,
            keywords_evidencia=json.dumps(resultado["keywords"]),
            modelo_usado="keyword_weighted_v2",
        )

        db.session.add(clasificacion)
        clasificaciones.append(clasificacion)
        explicaciones.append(explicacion)

    db.session.flush()

    return clasificaciones, explicaciones
