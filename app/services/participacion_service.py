from __future__ import annotations

from app import db
from app.errors import DatabaseError
from app.models.participacion import Participacion
from app.models.sector import Sector
from app.decorators import hash_ip
from app.services.srie_service import clasificar


def crear_participacion(data: dict, ip_address: str) -> Participacion:
    ip_hash_value = hash_ip(ip_address)
    tipo_propuesta = data.get('tipo_propuesta', 'unificada')

    clasificacion_srie = clasificar(data)

    if tipo_propuesta == 'por_sector' and data.get('propuestas'):
        return _crear_por_sector(data, ip_hash_value, clasificacion_srie)
    else:
        return _crear_unificada(data, ip_hash_value, clasificacion_srie)


def _crear_unificada(data: dict, ip_hash_value: str, clasificacion_srie: dict) -> Participacion:
    participacion = Participacion(
        departamento=data.get('departamento', ''),
        municipio=data.get('municipio', ''),
        rango_edad=data.get('rango_edad', ''),
        genero=data.get('genero', ''),
        sector_prioritario_id=data.get('sector_prioritario_id'),
        problema_principal=data.get('problema_principal', ''),
        problema_otro=data.get('problema_otro', ''),
        contexto_ciudadano=data.get('contexto_ciudadano', ''),
        actores_responsables=data.get('actores_responsables', ''),
        beneficiarios=data.get('beneficiarios', ''),
        propuesta=data.get('propuesta', ''),
        srie_pilar=clasificacion_srie['pilar']['nombre'],
        srie_urgencia=clasificacion_srie['urgencia']['nivel'],
        srie_impacto=clasificacion_srie['impacto']['nivel'],
        srie_explicacion=clasificacion_srie['explicacion'],
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


def _crear_por_sector(data: dict, ip_hash_value: str, clasificacion_srie: dict) -> Participacion:
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
                contexto_ciudadano=data.get('contexto_ciudadano', ''),
                actores_responsables=data.get('actores_responsables', ''),
                beneficiarios=data.get('beneficiarios', ''),
                propuesta=propuesta_texto,
                srie_pilar=clasificacion_srie['pilar']['nombre'],
                srie_urgencia=clasificacion_srie['urgencia']['nivel'],
                srie_impacto=clasificacion_srie['impacto']['nivel'],
                srie_explicacion=clasificacion_srie['explicacion'],
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
    sectores = Sector.query.filter(Sector.id.in_(sectores_ids)).all()
    participacion.sectores = sectores
