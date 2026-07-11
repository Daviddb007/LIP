"""Servicio de armonización entre participación ciudadana, políticas públicas y ODS.

Construye una matriz de cobertura sectorial, identifica brechas (gaps),
coincidencias y oportunidades, y mapea la relación con los 17 ODS.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Any

from app import db
from app.models.catalog import Sector, Subsector, ProblemaCatalogo, participacion_problemas
from app.models.participacion import Participacion
from app.models.politica import Politica
from app.models.plan import Pilar
from sqlalchemy import func

ODS_INFO: dict[str, dict] = {
    '1': {'nombre': 'Fin de la pobreza', 'color': '#e5243b'},
    '2': {'nombre': 'Hambre cero', 'color': '#dda63a'},
    '3': {'nombre': 'Salud y bienestar', 'color': '#4c9f38'},
    '4': {'nombre': 'Educación de calidad', 'color': '#c5192d'},
    '5': {'nombre': 'Igualdad de género', 'color': '#ff3a21'},
    '6': {'nombre': 'Agua limpia y saneamiento', 'color': '#26bde2'},
    '7': {'nombre': 'Energía asequible', 'color': '#fcc30b'},
    '8': {'nombre': 'Trabajo decente', 'color': '#a21942'},
    '9': {'nombre': 'Industria e innovación', 'color': '#fd6925'},
    '10': {'nombre': 'Reducción de desigualdades', 'color': '#dd1367'},
    '11': {'nombre': 'Ciudades sostenibles', 'color': '#fd9d24'},
    '12': {'nombre': 'Producción responsables', 'color': '#bf8b2e'},
    '13': {'nombre': 'Acción por el clima', 'color': '#3f7e44'},
    '14': {'nombre': 'Vida submarina', 'color': '#0a97d9'},
    '15': {'nombre': 'Vida de ecosistemas', 'color': '#56c02b'},
    '16': {'nombre': 'Paz y justicia', 'color': '#00689d'},
    '17': {'nombre': 'Alianzas para lograr objetivos', 'color': '#19486a'},
}

SECTOR_ODS_MAP: dict[str, list[str]] = {
    'Economía y empleo': ['8', '9', '10'],
    'Seguridad': ['16'],
    'Educación': ['4', '10'],
    'Salud': ['3'],
    'Infraestructura': ['9', '11'],
    'Medio ambiente': ['13', '14', '15'],
    'Tecnología': ['9'],
    'Agricultura': ['2', '12'],
    'Juventud': ['4', '8'],
    'Emprendimiento': ['8', '9'],
    'Cultura': ['11'],
    'Lucha contra la corrupción': ['16'],
}


def generar_armonizacion() -> dict[str, Any]:
    """Genera el reporte completo de armonización: matriz, ODS, gaps, coincidencias y oportunidades."""
    sectores = _stats_participacion_por_sector()
    politicas = _stats_politicas_por_sector()
    srie_pilares = _stats_srie_pilares()
    total_participaciones = Participacion.query.count()
    total_politicas = Politica.query.filter_by(activo=True).count()

    matriz = _construir_matriz(sectores, politicas)
    ods = _analizar_ods(politicas)

    gaps = _identificar_gaps(matriz)
    coincidencias = _identificar_coincidencias(matriz)
    oportunidades = _identificar_oportunidades(matriz, politicas)

    return {
        'resumen': {
            'total_participaciones': total_participaciones,
            'total_politicas': total_politicas,
            'sectores_activos': len(sectores),
            'sectores_con_politica': len(politicas),
            'total_gaps': len(gaps),
            'total_coincidencias': len(coincidencias),
            'total_oportunidades': len(oportunidades),
        },
        'matriz': matriz,
        'srie_pilares': srie_pilares,
        'ods': ods,
        'gaps': gaps,
        'coincidencias': coincidencias,
        'oportunidades': oportunidades,
    }


def _stats_participacion_por_sector() -> dict[str, int]:
    """Cuenta participaciones únicas agrupadas por sector a través de la jerarquía problema → subsector → sector."""
    rows = (
        db.session.query(Sector.nombre, func.count(func.distinct(Participacion.id)))
        .join(Subsector, Subsector.sector_id == Sector.id)
        .join(ProblemaCatalogo, ProblemaCatalogo.subsector_id == Subsector.id)
        .join(participacion_problemas, participacion_problemas.c.problema_id == ProblemaCatalogo.id)
        .join(Participacion, Participacion.id == participacion_problemas.c.participacion_id)
        .group_by(Sector.id, Sector.nombre)
        .all()
    )
    return {nombre: total for nombre, total in rows}


def _stats_politicas_por_sector() -> dict[str, list[Politica]]:
    """Agrupa políticas activas por nombre de sector."""
    result: dict[str, list[Politica]] = defaultdict(list)
    politicas = Politica.query.filter_by(activo=True).all()
    for p in politicas:
        if p.sector:
            result[p.sector.nombre].append(p)
        else:
            result['General'].append(p)
    return dict(result)


def _stats_srie_pilares() -> list[dict]:
    """Cuenta clasificaciones SRIE agrupadas por nombre del pilar."""
    from app.models.participacion import ClasificacionSRIE

    rows = (
        db.session.query(Pilar.nombre, func.count(ClasificacionSRIE.id))
        .join(ClasificacionSRIE.pilar)
        .group_by(Pilar.id, Pilar.nombre)
        .order_by(func.count(ClasificacionSRIE.id).desc())
        .all()
    )
    return [{'nombre': nombre, 'total': total} for nombre, total in rows]


def _construir_matriz(
    sectores: dict[str, int],
    politicas: dict[str, list],
) -> list[dict]:
    """Construye la matriz de cobertura sectorial combinando datos de participación y políticas."""
    todos_sectores = set(list(sectores.keys()) + list(politicas.keys()))
    sectores_ordenados = sorted(
        todos_sectores,
        key=lambda s: sectores.get(s, 0),
        reverse=True,
    )

    max_participaciones = max(sectores.values()) if sectores else 1
    max_politicas = max(
        (len(p) for p in politicas.values()), default=1
    )

    matriz: list[dict] = []
    for nombre in sectores_ordenados:
        participaciones = sectores.get(nombre, 0)
        politicas_sector = politicas.get(nombre, [])
        num_politicas = len(politicas_sector)

        nivel_prioridad = _calcular_nivel(participaciones, max_participaciones)
        nivel_cobertura = _calcular_nivel(num_politicas, max_politicas)

        if participaciones > 0 and num_politicas == 0:
            estado = 'vacio'
            label = 'Vacío'
        elif participaciones > 0 and num_politicas > 0:
            estado = 'armonico'
            label = 'Armónico'
        elif participaciones == 0 and num_politicas > 0:
            estado = 'potencial'
            label = 'Potencial'
        else:
            estado = 'sin_datos'
            label = 'Sin datos'

        matriz.append({
            'sector': nombre,
            'participaciones': participaciones,
            'politicas': num_politicas,
            'nivel_prioridad': nivel_prioridad,
            'nivel_cobertura': nivel_cobertura,
            'estado': estado,
            'label': label,
            'ods_relacionados': SECTOR_ODS_MAP.get(nombre, []),
        })

    return matriz


def _calcular_nivel(valor: int, maximo: int) -> str:
    """Clasifica un valor como alto/medio/bajo según su proporción del máximo."""
    if maximo == 0:
        return 'bajo'
    proporcion = valor / maximo
    if proporcion >= 0.66:
        return 'alto'
    elif proporcion >= 0.33:
        return 'medio'
    return 'bajo'


def _analizar_ods(politicas: dict[str, list]) -> list[dict]:
    """Analiza qué ODS están cubiertos por las políticas activas."""
    ods_counts: dict[str, int] = defaultdict(int)
    for sector_nombre, politicas_sector in politicas.items():
        for p in politicas_sector:
            if p.ods_relacionados:
                for ods_id in p.ods_relacionados.split(','):
                    ods_id = ods_id.strip()
                    if ods_id in ODS_INFO:
                        ods_counts[ods_id] += 1

    result = []
    for ods_id, count in sorted(ods_counts.items(), key=lambda x: x[1], reverse=True):
        info = ODS_INFO.get(ods_id, {})
        result.append({
            'id': ods_id,
            'nombre': info.get('nombre', ''),
            'color': info.get('color', '#94a3b8'),
            'politicas_relacionadas': count,
        })

    ids_con_datos = set(ods_counts.keys())
    for ods_id, info in ODS_INFO.items():
        if ods_id not in ids_con_datos:
            result.append({
                'id': ods_id,
                'nombre': info['nombre'],
                'color': info['color'],
                'politicas_relacionadas': 0,
            })

    return result


def _identificar_gaps(matriz: list[dict]) -> list[dict]:
    """Identifica sectores con participación ciudadana pero sin política pública (brechas)."""
    return [
        {
            'sector': m['sector'],
            'participaciones': m['participaciones'],
            'nivel_prioridad': m['nivel_prioridad'],
            'ods_recomendados': m['ods_relacionados'],
            'mensaje': f"Los ciudadanos han manifestado {m['participaciones']} preocupaciones en {m['sector']}, pero no existe una política pública formal que las atienda.",
        }
        for m in matriz
        if m['estado'] == 'vacio'
    ]


def _identificar_coincidencias(matriz: list[dict]) -> list[dict]:
    """Identifica sectores donde hay alineación entre participación y políticas."""
    return [
        {
            'sector': m['sector'],
            'participaciones': m['participaciones'],
            'politicas': m['politicas'],
            'nivel_cobertura': m['nivel_cobertura'],
            'mensaje': f"Existe alineación entre la preocupación ciudadana y las {m['politicas']} política(s) pública(s) existentes en {m['sector']}.",
        }
        for m in matriz
        if m['estado'] == 'armonico'
    ]


def _identificar_oportunidades(
    matriz: list[dict],
    politicas: dict[str, list],
) -> list[dict]:
    """Identifica sectores con políticas existentes que podrían beneficiarse de más participación."""
    oportunidades: list[dict] = []
    for m in matriz:
        if m['estado'] == 'potencial':
            politicas_sector = politicas.get(m['sector'], [])
            nombres_politicas = [p.titulo for p in politicas_sector[:3]]
            oportunidades.append({
                'sector': m['sector'],
                'politicas': nombres_politicas,
                'total_politicas': m['politicas'],
                'mensaje': f"Existen {m['politicas']} política(s) en {m['sector']} que podrían beneficiarse de participación ciudadana para su fortalecimiento.",
            })
    return oportunidades
