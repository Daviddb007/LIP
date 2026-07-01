from __future__ import annotations

from typing import Any

from app import db
from app.models.participacion import Participacion
from app.models.sector import Sector
from sqlalchemy import func


def get_estadisticas_generales() -> dict[str, Any]:
    """Return high-level participation statistics for the home page."""
    return {
        'total_participaciones': Participacion.query.count(),
        'total_departamentos': _count_distinct_departamentos(),
        'total_sectores': Sector.query.filter_by(activo=True).count(),
    }


def get_estadisticas_completas() -> dict[str, Any]:
    """Return full statistics for the public results page."""
    return {
        'total_participaciones': Participacion.query.count(),
        'total_departamentos': _count_distinct_departamentos(),
        'sectores': _stats_por_sector(),
        'problemas': _stats_por_problema(),
        'departamentos': _stats_por_departamento(),
        'tendencia': _tendencia_diaria(),
        'propuestas_recientes': _propuestas_recientes(),
    }


def _count_distinct_departamentos() -> int:
    return db.session.query(
        func.count(db.distinct(Participacion.departamento))
    ).scalar()


def _stats_por_sector() -> list[dict]:
    rows = (
        db.session.query(Sector.nombre, func.count(Participacion.id))
        .join(Participacion.sectores)
        .group_by(Sector.nombre)
        .order_by(func.count(Participacion.id).desc())
        .all()
    )
    return [{'nombre': nombre, 'total': total} for nombre, total in rows]


def _stats_por_problema() -> list[dict]:
    rows = (
        db.session.query(
            Participacion.problema_principal, func.count(Participacion.id)
        )
        .filter(
            Participacion.problema_principal.isnot(None),
            Participacion.problema_principal != '',
        )
        .group_by(Participacion.problema_principal)
        .order_by(func.count(Participacion.id).desc())
        .limit(10)
        .all()
    )
    return [{'nombre': nombre, 'total': total} for nombre, total in rows]


def _stats_por_departamento() -> list[dict]:
    rows = (
        db.session.query(
            Participacion.departamento, func.count(Participacion.id)
        )
        .filter(
            Participacion.departamento.isnot(None),
            Participacion.departamento != '',
        )
        .group_by(Participacion.departamento)
        .order_by(func.count(Participacion.id).desc())
        .all()
    )
    return [{'nombre': nombre, 'total': total} for nombre, total in rows]


def _tendencia_diaria() -> list[dict]:
    rows = (
        db.session.query(
            func.date(Participacion.created_at), func.count(Participacion.id)
        )
        .group_by(func.date(Participacion.created_at))
        .order_by(func.date(Participacion.created_at))
        .limit(30)
        .all()
    )
    return [{'fecha': str(fecha), 'total': total} for fecha, total in rows]


def _propuestas_recientes() -> list[dict]:
    participaciones = (
        Participacion.query
        .order_by(Participacion.created_at.desc())
        .limit(5)
        .all()
    )
    return [p.to_recent_dict() for p in participaciones]
