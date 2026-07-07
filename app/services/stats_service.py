from __future__ import annotations

from typing import Any

from app import db
from app.models.participacion import Participacion
from app.models.sector import Sector
from app.models.politica import Politica
from sqlalchemy import func


def get_estadisticas_generales() -> dict[str, Any]:
    return {
        'total_participaciones': Participacion.query.count(),
        'total_departamentos': _count_distinct_departamentos(),
        'total_sectores': Sector.query.filter_by(activo=True).count(),
    }


def get_estadisticas_completas() -> dict[str, Any]:
    return {
        'total_participaciones': Participacion.query.count(),
        'total_departamentos': _count_distinct_departamentos(),
        'total_politicas': Politica.query.filter_by(activo=True).count(),
        'sectores': _stats_por_sector(),
        'problemas': _stats_por_problema(),
        'departamentos': _stats_por_departamento(),
        'tendencia': _tendencia_diaria(),
        'propuestas_recientes': _propuestas_recientes(),
        'srie_pilares': _stats_srie_pilares(),
        'srie_urgencia': _stats_srie_urgencia(),
        'srie_impacto': _stats_srie_impacto(),
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


def _stats_srie_pilares() -> list[dict]:
    rows = (
        db.session.query(
            Participacion.srie_pilar, func.count(Participacion.id)
        )
        .filter(
            Participacion.srie_pilar.isnot(None),
            Participacion.srie_pilar != '',
        )
        .group_by(Participacion.srie_pilar)
        .order_by(func.count(Participacion.id).desc())
        .all()
    )
    return [{'nombre': nombre, 'total': total} for nombre, total in rows]


def _stats_srie_urgencia() -> list[dict]:
    orden = {
        'Crítica': 1,
        'Alta': 2,
        'Moderada': 3,
        'Baja': 4,
    }
    rows = (
        db.session.query(
            Participacion.srie_urgencia, func.count(Participacion.id)
        )
        .filter(
            Participacion.srie_urgencia.isnot(None),
            Participacion.srie_urgencia != '',
        )
        .group_by(Participacion.srie_urgencia)
        .all()
    )
    result = [{'nombre': nombre, 'total': total} for nombre, total in rows]
    result.sort(key=lambda x: orden.get(x['nombre'], 99))
    return result


def _stats_srie_impacto() -> list[dict]:
    orden = {
        'Nacional': 1,
        'Regional': 2,
        'Local': 3,
    }
    rows = (
        db.session.query(
            Participacion.srie_impacto, func.count(Participacion.id)
        )
        .filter(
            Participacion.srie_impacto.isnot(None),
            Participacion.srie_impacto != '',
        )
        .group_by(Participacion.srie_impacto)
        .all()
    )
    result = [{'nombre': nombre, 'total': total} for nombre, total in rows]
    result.sort(key=lambda x: orden.get(x['nombre'], 99))
    return result
