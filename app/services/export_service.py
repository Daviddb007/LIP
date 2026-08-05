"""Servicio de exportación de datos en formato CSV con paginación para grandes volúmenes.

Utiliza iteración paginada (100 registros por página) para minimizar el uso de memoria.
"""
from __future__ import annotations

import csv
import io
from typing import Any, Iterator

from app.models.participacion import Participacion


def exportar_participaciones_csv() -> str:
    """Exporta todas las participaciones como string CSV con streaming paginado."""
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        'ID', 'Fecha', 'Departamento', 'Municipio', 'Zona', 'Rango Edad',
        'Género', 'Problemas', 'Propuesta', 'Pilar', 'Confianza', 'IP Hash',
    ])

    for participacion in _iter_participaciones():
        writer.writerow(_to_csv_row(participacion))

    output.seek(0)
    return output.getvalue()


def _to_csv_row(p: Participacion) -> list[Any]:
    """Convierte una participación en una fila de CSV con los campos requeridos."""
    pilar = p.clasificaciones[0].pilar.nombre if p.clasificaciones else ''
    confianza = p.clasificaciones[0].confianza if p.clasificaciones else ''

    from app.models.catalog import participacion_problemas, ProblemaCatalogo
    problemas = ProblemaCatalogo.query.join(
        participacion_problemas,
        participacion_problemas.c.problema_id == ProblemaCatalogo.id,
    ).filter(participacion_problemas.c.participacion_id == p.id).all()
    problemas_str = '; '.join(pr.nombre for pr in problemas)

    return [
        p.id,
        p.created_at.strftime('%Y-%m-%d %H:%M:%S') if p.created_at else '',
        p.departamento,
        p.municipio,
        p.zona,
        p.rango_edad or '',
        p.genero or '',
        problemas_str,
        p.propuesta,
        pilar,
        confianza,
        p.ip_hash or '',
    ]


def _iter_participaciones() -> Iterator[Participacion]:
    """Itera sobre todas las participaciones usando paginación (100 por página)."""
    page = 1
    per_page = 100

    while True:
        paginated = Participacion.query.order_by(
            Participacion.created_at.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)

        yield from paginated.items

        if not paginated.has_next:
            break
        page += 1
