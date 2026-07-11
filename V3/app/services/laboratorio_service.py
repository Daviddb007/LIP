"""Servicio del laboratorio de simulación para modelar escenarios de inversión pública.

Calcula el estado actual de armonía sectorial y permite simular
redistribuciones de presupuesto, nuevos sectores y cambios en participación.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Any

from app import db
from app.models.catalog import Sector, Subsector, ProblemaCatalogo, participacion_problemas
from app.models.participacion import Participacion
from app.models.politica import Politica
from sqlalchemy import func

PESO_PRESUPUESTO: float = 0.4
PESO_PARTICIPACION: float = 0.3
PESO_POLITICAS: float = 0.3


def estado_actual() -> dict[str, Any]:
    """Retorna el estado actual de todos los sectores con su índice de armonía."""
    sectores = _datos_sectores()
    total_part = sum(s['participaciones'] for s in sectores)
    total_pol = sum(s['politicas'] for s in sectores)

    return {
        'sectores': sectores,
        'total_participaciones': total_part,
        'total_politicas': total_pol,
        'indice_armonia': _calcular_indice_armonia(sectores),
    }


def simular(params: dict) -> dict[str, Any]:
    """Ejecuta una simulación con parámetros de presupuesto, redistribución y nuevos sectores."""
    datos_base = _datos_sectores()
    presupuesto_extra = params.get('presupuesto_extra', 0)
    redistribuir_hacia = params.get('redistribuir_hacia', '')
    porcentaje_redistribucion = params.get('porcentaje_redistribucion', 0)
    nuevo_sector = params.get('nuevo_sector', '')
    nuevas_participaciones = params.get('nuevas_participaciones', 0)

    sim_sectores: list[dict] = []
    for s in datos_base:
        sim = dict(s)

        if redistribuir_hacia and s['nombre'] == redistribuir_hacia:
            impacto_presupuesto = _impacto_presupuesto(s, presupuesto_extra * (porcentaje_redistribucion / 100))
            sim['participaciones_proyectadas'] = int(s['participaciones'] * (1 + impacto_presupuesto))
            sim['presupuesto_simulado'] = int(s.get('presupuesto_estimado', 0) + presupuesto_extra * (porcentaje_redistribucion / 100))
        else:
            impacto_presupuesto = _impacto_presupuesto(s, presupuesto_extra * (1 / max(len(datos_base), 1)))
            sim['participaciones_proyectadas'] = int(s['participaciones'] * (1 + impacto_presupuesto))
            sim['presupuesto_simulado'] = int(s.get('presupuesto_estimado', 0))

        sim['cambio_participacion'] = sim['participaciones_proyectadas'] - s['participaciones']
        sim['cambio_porcentual'] = round(
            ((sim['participaciones_proyectadas'] - s['participaciones']) / max(s['participaciones'], 1)) * 100, 1
        )

        sim_sectores.append(sim)

    if nuevo_sector and nuevas_participaciones > 0:
        sim_sectores.append(_sector_nuevo(nuevo_sector, nuevas_participaciones))

    total_part_proy = sum(s['participaciones_proyectadas'] for s in sim_sectores)

    ganadores = [s for s in sim_sectores if s['cambio_participacion'] > 0]
    perdedores = [s for s in sim_sectores if s['cambio_participacion'] < 0]

    indice_armonia_base = _calcular_indice_armonia(datos_base)
    indice_armonia_sim = _calcular_indice_armonia(sim_sectores)

    return {
        'sectores': sim_sectores,
        'resumen': {
            'total_participaciones_base': sum(s['participaciones'] for s in datos_base),
            'total_participaciones_simulado': total_part_proy,
            'total_politicas': sum(s['politicas'] for s in datos_base),
            'cambio_total': total_part_proy - sum(s['participaciones'] for s in datos_base),
            'ganadores': len(ganadores),
            'perdedores': len(perdedores),
            'indice_armonia_base': indice_armonia_base,
            'indice_armonia_sim': indice_armonia_sim,
            'cambio_armonia': round(indice_armonia_sim - indice_armonia_base, 2),
        }
    }


def _datos_sectores() -> list[dict]:
    """Obtiene datos consolidados de todos los sectores: participaciones, políticas y presupuesto estimado."""
    participaciones = (
        db.session.query(Sector.nombre, func.count(func.distinct(Participacion.id)))
        .join(Subsector, Subsector.sector_id == Sector.id)
        .join(ProblemaCatalogo, ProblemaCatalogo.subsector_id == Subsector.id)
        .join(participacion_problemas, participacion_problemas.c.problema_id == ProblemaCatalogo.id)
        .join(Participacion, Participacion.id == participacion_problemas.c.participacion_id)
        .group_by(Sector.id, Sector.nombre)
        .all()
    )
    part_dict = dict(participaciones)

    politicas: dict[str, list[Politica]] = defaultdict(list)
    for p in Politica.query.filter_by(activo=True).all():
        if p.sector:
            politicas[p.sector.nombre].append(p)

    todos = set(list(part_dict.keys()) + list(politicas.keys()))

    result: list[dict] = []
    for nombre in sorted(todos):
        num_part = part_dict.get(nombre, 0)
        lista_pol = politicas.get(nombre, [])
        result.append({
            'nombre': nombre,
            'participaciones': num_part,
            'politicas': len(lista_pol),
            'nombres_politicas': [p.titulo for p in lista_pol[:3]],
            'presupuesto_estimado': _estimar_presupuesto(nombre, len(lista_pol)),
            'participaciones_proyectadas': num_part,
            'cambio_participacion': 0,
            'cambio_porcentual': 0,
        })

    return result


def _estimar_presupuesto(sector: str, num_politicas: int) -> int:
    """Estima el presupuesto de un sector basado en valores de referencia y número de políticas."""
    base_presupuesto: dict[str, int] = {
        'Economía y empleo': 5000,
        'Seguridad': 8000,
        'Educación': 6000,
        'Salud': 7000,
        'Infraestructura': 4000,
        'Medio ambiente': 2000,
        'Tecnología': 1500,
        'Agricultura': 2500,
        'Juventud': 1000,
        'Emprendimiento': 800,
        'Cultura': 500,
        'Lucha contra la corrupción': 300,
    }
    base = base_presupuesto.get(sector, 1000)
    return base + (num_politicas * 500)


def _impacto_presupuesto(sector: dict, monto_extra: float) -> float:
    """Calcula el impacto de una inyección presupuestal en la participación proyectada."""
    presupuesto_base = sector.get('presupuesto_estimado', 1000) or 1000
    incremento = monto_extra / presupuesto_base if presupuesto_base > 0 else 0
    return min(incremento * PESO_PRESUPUESTO, 0.5)


def _sector_nuevo(nombre: str, participaciones: int) -> dict:
    """Crea un sector nuevo para la simulación con valores por defecto."""
    return {
        'nombre': nombre,
        'participaciones': 0,
        'politicas': 0,
        'nombres_politicas': [],
        'presupuesto_estimado': 500,
        'participaciones_proyectadas': participaciones,
        'cambio_participacion': participaciones,
        'cambio_porcentual': 100,
    }


def _calcular_indice_armonia(sectores: list[dict]) -> float:
    """Calcula el índice de armonía global: qué tan balanceada está la relación participación ↔ políticas."""
    if not sectores:
        return 0

    total_part = sum(s['participaciones'] for s in sectores) or 1
    total_pol = sum(s['politicas'] for s in sectores) or 1

    puntajes: list[float] = []
    for s in sectores:
        proporcion_part = s['participaciones'] / total_part
        proporcion_pol = s['politicas'] / total_pol if total_pol > 0 else 0
        if proporcion_part > 0 or proporcion_pol > 0:
            armonia = 1 - abs(proporcion_part - proporcion_pol)
            puntajes.append(armonia)

    if not puntajes:
        return 0

    return round((sum(puntajes) / len(puntajes)) * 100, 1)
