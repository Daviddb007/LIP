from __future__ import annotations

import logging

from app import db
from app.models.sector import Sector
from app.models.problema import Problema

logger = logging.getLogger(__name__)

SECTORES: list[dict[str, str]] = [
    {'nombre': 'Economía y empleo', 'icono': 'briefcase'},
    {'nombre': 'Seguridad', 'icono': 'shield-check'},
    {'nombre': 'Educación', 'icono': 'book'},
    {'nombre': 'Salud', 'icono': 'heart-pulse'},
    {'nombre': 'Infraestructura', 'icono': 'building'},
    {'nombre': 'Medio ambiente', 'icono': 'tree'},
    {'nombre': 'Tecnología', 'icono': 'laptop'},
    {'nombre': 'Agricultura', 'icono': 'farm'},
    {'nombre': 'Juventud', 'icono': 'people'},
    {'nombre': 'Emprendimiento', 'icono': 'rocket'},
    {'nombre': 'Cultura', 'icono': 'palette'},
    {'nombre': 'Lucha contra la corrupción', 'icono': 'shield-x'},
]

PROBLEMAS_POR_SECTOR: dict[str, list[str]] = {
    'Economía y empleo': [
        'Desempleo', 'Informalidad', 'Bajos salarios', 'Pocas oportunidades',
    ],
    'Seguridad': [
        'Inseguridad ciudadana', 'Crimen organizado',
        'Violencia doméstica', 'Delitos informáticos',
    ],
    'Educación': [
        'Falta de acceso a educación superior', 'Calidad de la educación básica',
        'Brecha digital educativa', 'Falta de formación técnica',
    ],
    'Salud': [
        'Falta de acceso a servicios de salud', 'Calidad del sistema de salud',
        'Falta de profesionales en zonas rurales', 'Costos altos de medicamentos',
    ],
    'Infraestructura': [
        'Falta de vías de acceso', 'Déficit de vivienda',
        'Problemas de acueducto y alcantarillado', 'Falta de energía en zonas rurales',
    ],
    'Medio ambiente': [
        'Contaminación del agua', 'Deforestación',
        'Falta de gestión de residuos', 'Cambio climático',
    ],
    'Tecnología': [
        'Brecha digital', 'Falta de conectividad en zonas rurales',
        'Baja adopción tecnológica en empresas', 'Ciberseguridad',
    ],
    'Agricultura': [
        'Falta de financiación para agricultores', 'Baja productividad',
        'Falta de infraestructura de riego', 'Precios injustos para productores',
    ],
    'Juventud': [
        'Desempleo juvenil', 'Falta de oportunidades de formación',
        'Consumo de sustancias psicoactivas', 'Falta de espacios recreativos',
    ],
    'Emprendimiento': [
        'Falta de financiación', 'Trámites burocráticos complejos',
        'Falta de acompañamiento técnico', 'Acceso limitado a mercados',
    ],
    'Cultura': [
        'Falta de presupuesto para cultura', 'Poca valoración del patrimonio cultural',
        'Falta de espacios culturales', 'Preservación de tradiciones',
    ],
    'Lucha contra la corrupción': [
        'Falta de transparencia en la gestión pública', 'Impunidad',
        'Mal uso de recursos públicos', 'Falta de controles ciudadanos',
    ],
}


def seed_database() -> None:
    """Populate the database with initial sectors and problems if empty."""

    if Sector.query.count() > 0:
        return

    _seed_sectores()
    _seed_problemas()
    logger.info('Base de datos inicializada con sectores y problemas.')


def _seed_sectores() -> None:
    """Insert initial sectors."""

    for sector_data in SECTORES:
        sector = Sector(
            nombre=sector_data['nombre'],
            icono=sector_data['icono'],
            activo=True,
        )
        db.session.add(sector)

    db.session.commit()


def _seed_problemas() -> None:
    """Insert problems for each sector."""

    for sector in Sector.query.all():
        problemas = PROBLEMAS_POR_SECTOR.get(sector.nombre, [])
        for nombre in problemas:
            problema = Problema(
                sector_id=sector.id,
                nombre=nombre,
                activo=True,
            )
            db.session.add(problema)

    db.session.commit()
