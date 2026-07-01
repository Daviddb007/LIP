from __future__ import annotations

import csv
import io
from typing import Iterator

from app.models.participacion import Participacion


def exportar_participaciones_csv() -> str:
    """Export all participations as a CSV string.

    Uses streaming to handle large datasets efficiently.
    """
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        'ID', 'Fecha', 'Departamento', 'Municipio', 'Rango Edad',
        'Género', 'Sector Prioritario', 'Problema Principal',
        'Propuesta', 'IP Hash',
    ])

    for participacion in _iter_participaciones():
        writer.writerow(participacion.to_csv_row())

    output.seek(0)
    return output.getvalue()


def _iter_participaciones() -> Iterator[Participacion]:
    """Yield participations one at a time to reduce memory usage."""
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
