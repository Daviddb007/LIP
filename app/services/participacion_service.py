from __future__ import annotations

from app import db
from app.errors import DatabaseError
from app.models.participacion import Participacion
from app.models.sector import Sector
from app.decorators import hash_ip


def crear_participacion(data: dict, ip_address: str) -> Participacion:
    """Create and persist a new participation record.
    
    For per-sector proposals, creates one Participacion per sector.
    For unified proposals, creates a single Participacion.
    """
    ip_hash_value = hash_ip(ip_address)
    tipo_propuesta = data.get('tipo_propuesta', 'unificada')

    if tipo_propuesta == 'por_sector' and data.get('propuestas'):
        return _crear_por_sector(data, ip_hash_value)
    else:
        return _crear_unificada(data, ip_hash_value)


def _crear_unificada(data: dict, ip_hash_value: str) -> Participacion:
    """Create a single participation with unified proposal."""
    participacion = Participacion(
        departamento=data.get('departamento', ''),
        municipio=data.get('municipio', ''),
        rango_edad=data.get('rango_edad', ''),
        genero=data.get('genero', ''),
        sector_prioritario_id=data.get('sector_prioritario_id'),
        problema_principal=data.get('problema_principal', ''),
        problema_otro=data.get('problema_otro', ''),
        propuesta=data.get('propuesta', ''),
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


def _crear_por_sector(data: dict, ip_hash_value: str) -> Participacion:
    """Create one participation per sector with per-sector proposals."""
    propuestas = data.get('propuestas', [])
    sectores_ids = data.get('sectores', [])
    first_participacion = None

    try:
        for item in propuestas:
            sector_id = item.get('sector_id')
            propuesta_texto = item.get('propuesta', '')

            participacion = Participacion(
                departamento=data.get('departamento', ''),
                municipio=data.get('municipio', ''),
                rango_edad=data.get('rango_edad', ''),
                genero=data.get('genero', ''),
                sector_prioritario_id=sector_id,
                problema_principal=data.get('problema_principal', ''),
                problema_otro=data.get('problema_otro', ''),
                propuesta=propuesta_texto,
                ip_hash=ip_hash_value,
            )

            _attach_sectores(participacion, [sector_id] if sector_id else sectores_ids)
            db.session.add(participacion)

            if first_participacion is None:
                first_participacion = participacion

        db.session.commit()
    except Exception:
        db.session.rollback()
        raise DatabaseError('Error al guardar la participación')

    return first_participacion


def _attach_sectores(participacion: Participacion, sectores_ids: list[int]) -> None:
    """Load and attach sector relationships to a participation."""
    sectores = Sector.query.filter(Sector.id.in_(sectores_ids)).all()
    participacion.sectores = sectores
