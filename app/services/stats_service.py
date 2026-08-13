"""Servicio de estadísticas generales y dashboard para el panel de administración.

Proporciona consultas agregadas sobre participaciones, sectores, problemas,
departamentos, tendencias temporales, propuestas recientes y clasificaciones SRIE.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from app import cache, db
from app.models.catalog import (
    Actor,
    Sector,
    Subsector,
    ProblemaCatalogo,
    participacion_actores,
    participacion_problemas,
)
from app.models.participacion import Participacion, ClasificacionSRIE
from app.models.plan import Pilar
from app.models.politica import Politica
from app.services.db_helpers import date_trunc
from sqlalchemy import desc, func


def get_estadisticas_generales() -> dict[str, int]:
    """Retorna estadísticas generales (totales) con caché de 1 hora.

    Returns:
        dict con total_participaciones, total_departamentos, total_sectores.
    """
    cached = cache.get("estadisticas_generales")
    if cached is not None:
        return cached

    total_participaciones = db.session.query(func.count(Participacion.id)).scalar() or 0
    total_departamentos = (
        db.session.query(func.count(func.distinct(Participacion.departamento)))
        .filter(
            Participacion.departamento.isnot(None),
            Participacion.departamento != "",
        )
        .scalar()
        or 0
    )
    total_sectores = (
        db.session.query(func.count(Sector.id)).filter(Sector.activo.is_(True)).scalar()
        or 0
    )

    result: dict[str, int] = {
        "total_participaciones": total_participaciones,
        "total_departamentos": total_departamentos,
        "total_sectores": total_sectores,
    }

    cache.set("estadisticas_generales", result, timeout=3600)
    return result


def get_estadisticas_completas() -> dict[str, Any]:
    """Retorna el conjunto completo de estadísticas para el dashboard.

    Incluye totales, distribución por sector/problema/departamento,
    tendencia diaria (30 días), propuestas recientes y clasificaciones SRIE.

    Returns:
        dict con todos los bloques de estadísticas.
    """
    total_participaciones = db.session.query(func.count(Participacion.id)).scalar() or 0
    total_departamentos = (
        db.session.query(func.count(func.distinct(Participacion.departamento)))
        .filter(
            Participacion.departamento.isnot(None),
            Participacion.departamento != "",
        )
        .scalar()
        or 0
    )
    total_politicas = (
        db.session.query(func.count(Politica.id))
        .filter(Politica.activo.is_(True))
        .scalar()
        or 0
    )

    # Stats por sector (M:N: Participacion -> participacion_problemas -> ProblemaCatalogo -> Subsector -> Sector)
    sectores = _get_sectores_stats()

    # Stats por problema (via participacion_problemas)
    problemas = _get_problemas_stats()

    # Stats por departamento
    departamentos = _get_departamentos_stats()

    # Tendencia diaria (últimos 30 días)
    tendencia = _get_tendencia_diaria()

    # Últimas 5 propuestas (con resumen ligero)
    propuestas_recientes = _get_propuestas_recientes()

    # SRIE stats por pilar
    srie_pilares = _get_srie_pilares_stats()

    # srie_urgencia y srie_impacto no están disponibles en V3
    srie_urgencia: list[dict[str, Any]] = []
    srie_impacto: list[dict[str, Any]] = []

    return {
        "total_participaciones": total_participaciones,
        "total_departamentos": total_departamentos,
        "total_politicas": total_politicas,
        "sectores": sectores,
        "problemas": problemas,
        "departamentos": departamentos,
        "tendencia": tendencia,
        "propuestas_recientes": propuestas_recientes,
        "srie_pilares": srie_pilares,
        "srie_urgencia": srie_urgencia,
        "srie_impacto": srie_impacto,
    }


def get_dashboard_stats() -> dict[str, Any]:
    """Estadísticas del dashboard de administración.

    Incluye totales, participación del mes, cobertura de pilares, confianza
    promedio de clasificación y los top de problemas y actores.

    Returns:
        dict con total, this_month, municipios, pilares, total_pilares,
        coverage, avg_confidence, top_problemas y top_actores.
    """
    from datetime import datetime, timezone as tz

    now = datetime.now(tz.utc).replace(tzinfo=None)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    total = db.session.query(func.count(Participacion.id)).scalar() or 0
    this_month = (
        db.session.query(func.count(Participacion.id))
        .filter(Participacion.created_at >= month_start)
        .scalar()
        or 0
    )
    municipios = (
        db.session.query(func.count(func.distinct(Participacion.municipio))).scalar() or 0
    )
    pilares_cubiertos = (
        db.session.query(func.count(func.distinct(ClasificacionSRIE.pilar_id))).scalar() or 0
    )
    total_pilares = db.session.query(func.count(Pilar.id)).filter(Pilar.activo.is_(True)).scalar() or 0
    raw_avg = db.session.query(func.avg(ClasificacionSRIE.confianza)).scalar() or 0
    avg_conf = round(float(raw_avg) * 100, 1)

    top_problemas = (
        db.session.query(
            ProblemaCatalogo.nombre,
            func.count(participacion_problemas.c.participacion_id).label("total"),
        )
        .join(
            participacion_problemas,
            participacion_problemas.c.problema_id == ProblemaCatalogo.id,
        )
        .group_by(ProblemaCatalogo.nombre)
        .order_by(desc("total"))
        .limit(5)
        .all()
    )

    top_actores = (
        db.session.query(
            Actor.nombre,
            func.count(participacion_actores.c.participacion_id).label("total"),
        )
        .join(
            participacion_actores,
            participacion_actores.c.actor_id == Actor.id,
        )
        .group_by(Actor.nombre)
        .order_by(desc("total"))
        .limit(5)
        .all()
    )

    return {
        "total": total,
        "this_month": this_month,
        "municipios": municipios,
        "pilares": pilares_cubiertos,
        "total_pilares": total_pilares,
        "coverage": round(pilares_cubiertos / total_pilares * 100) if total_pilares > 0 else 0,
        "avg_confidence": avg_conf,
        "top_problemas": [{"nombre": nombre, "total": total_x} for nombre, total_x in top_problemas],
        "top_actores": [{"nombre": nombre, "total": total_x} for nombre, total_x in top_actores],
    }


def _get_sectores_stats() -> list[dict[str, Any]]:
    """Distribución de participaciones agrupadas por sector a través de la cadena M:N."""
    rows = (
        db.session.query(Sector.nombre, func.count(Participacion.id))
        .join(
            participacion_problemas,
            Participacion.id == participacion_problemas.c.participacion_id,
        )
        .join(
            ProblemaCatalogo,
            participacion_problemas.c.problema_id == ProblemaCatalogo.id,
        )
        .join(Subsector)
        .join(Sector)
        .group_by(Sector.nombre)
        .order_by(func.count(Participacion.id).desc())
        .all()
    )
    return [{"nombre": nombre, "total": total} for nombre, total in rows]


def _get_problemas_stats() -> list[dict[str, Any]]:
    """Distribución de participaciones agrupadas por problema del catálogo."""
    rows = (
        db.session.query(
            ProblemaCatalogo.nombre, func.count(Participacion.id)
        )
        .join(
            participacion_problemas,
            Participacion.id == participacion_problemas.c.participacion_id,
        )
        .join(
            ProblemaCatalogo,
            participacion_problemas.c.problema_id == ProblemaCatalogo.id,
        )
        .group_by(ProblemaCatalogo.nombre)
        .order_by(func.count(Participacion.id).desc())
        .all()
    )
    return [{"nombre": nombre, "total": total} for nombre, total in rows]


def _get_departamentos_stats() -> list[dict[str, Any]]:
    """Distribución de participaciones agrupadas por departamento."""
    rows = (
        db.session.query(
            Participacion.departamento, func.count(Participacion.id)
        )
        .filter(
            Participacion.departamento.isnot(None),
            Participacion.departamento != "",
        )
        .group_by(Participacion.departamento)
        .order_by(func.count(Participacion.id).desc())
        .all()
    )
    return [{"nombre": nombre, "total": total} for nombre, total in rows]


def _get_tendencia_diaria() -> list[dict[str, Any]]:
    """Tendencia diaria de participaciones en los últimos 30 días."""
    fecha_limite = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=30)
    date_col = date_trunc("day", Participacion.created_at)
    rows = (
        db.session.query(date_col, func.count(Participacion.id))
        .filter(Participacion.created_at >= fecha_limite)
        .group_by(date_col)
        .order_by(date_col)
        .all()
    )
    return [{"fecha": str(fecha)[:10], "total": total} for fecha, total in rows]


def _get_propuestas_recientes() -> list[dict[str, Any]]:
    """Últimas 5 participaciones con datos para vista previa."""
    participaciones = (
        Participacion.query.order_by(Participacion.created_at.desc()).limit(5).all()
    )
    return [p.to_recent_dict() for p in participaciones]


def _get_srie_pilares_stats() -> list[dict[str, Any]]:
    """Distribución de clasificaciones SRIE agrupadas por pilar."""
    rows = (
        db.session.query(Pilar.nombre, func.count(ClasificacionSRIE.id))
        .join(Pilar, ClasificacionSRIE.pilar_id == Pilar.id)
        .group_by(Pilar.nombre)
        .order_by(func.count(ClasificacionSRIE.id).desc())
        .all()
    )
    return [{"nombre": nombre, "total": total} for nombre, total in rows]
