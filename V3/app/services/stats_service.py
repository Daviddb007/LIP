"""Servicio de estadísticas generales y dashboard para el panel de administración.

Proporciona consultas agregadas sobre participaciones, sectores, problemas,
departamentos, tendencias temporales, propuestas recientes y clasificaciones SRIE.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from app import cache, db
from app.models.catalog import (
    Sector,
    Subsector,
    ProblemaCatalogo,
    participacion_problemas,
)
from app.models.participacion import Participacion, ClasificacionSRIE
from app.models.plan import Pilar
from app.models.politica import Politica
from sqlalchemy import func


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
    fecha_limite = datetime.utcnow() - timedelta(days=30)
    rows = (
        db.session.query(
            func.date_trunc("day", Participacion.created_at),
            func.count(Participacion.id),
        )
        .filter(Participacion.created_at >= fecha_limite)
        .group_by(func.date_trunc("day", Participacion.created_at))
        .order_by(func.date_trunc("day", Participacion.created_at))
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
