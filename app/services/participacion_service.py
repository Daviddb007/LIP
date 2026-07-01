from __future__ import annotations

from app import db
from app.errors import DatabaseError
from app.models.participacion import Participacion
from app.models.sector import Sector
from app.decorators import hash_ip


def crear_participacion(data: dict, ip_address: str) -> Participacion:
    """Create and persist a new participation record."""

    ip_hash_value = hash_ip(ip_address)

    participacion = Participacion(
        departamento=data.get('departamento', ''),
        municipio=data.get('municipio', ''),
        rango_edad=data.get('rango_edad', ''),
        genero=data.get('genero', ''),
        sector_prioritario_id=data.get('sector_prioritario_id'),
        problema_principal=data.get('problema_principal', ''),
        problema_otro=data.get('problema_otro', ''),
        propuesta=data['propuesta'],
        ip_hash=ip_hash_value,
    )

    _attach_sectores(participacion, data.get('sectores', []))

    try:
        db.session.add(participacion)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise DatabaseError('Error al guardar la participación')

    return participacion


def _attach_sectores(participacion: Participacion, sectores_ids: list[int]) -> None:
    """Load and attach sector relationships to a participation."""
    sectores = Sector.query.filter(Sector.id.in_(sectores_ids)).all()
    participacion.sectores = sectores
