from __future__ import annotations

import re
from collections import Counter, defaultdict
from typing import Any

from app import db
from app.models.participacion import Participacion
from app.models.sector import Sector
from app.models.politica import Politica
from sqlalchemy import func

STOP_WORDS = {
    'de', 'la', 'que', 'el', 'en', 'y', 'a', 'los', 'del', 'se', 'las', 'por', 'un',
    'para', 'con', 'no', 'una', 'su', 'al', 'lo', 'como', 'más', 'pero', 'sus', 'le',
    'ya', 'este', 'entre', 'porque', 'este', 'esta', 'estos', 'estas', 'ese', 'esa',
    'eso', 'todo', 'todos', 'toda', 'todas', 'muy', 'sin', 'sobre', 'también', 'otro',
    'otros', 'otra', 'otras', 'cada', 'tanto', 'tan', 'donde', 'cuando', 'cual',
    'quien', 'durante', 'después', 'antes', 'contra', 'hasta', 'desde', 'bajo',
    'entre', 'mediante', 'excepto', 'incluso', 'además', 'ambos', 'ambas',
}


def obtener_analitica() -> dict[str, Any]:
    palabras = _extraer_palabras()
    clusters = _generar_clusters()
    tendencias = _tendencia_mensual()
    territorio = _analisis_territorial()
    comparativas = _comparativas_sector()
    predicciones = _predicciones()

    return {
        'nube_palabras': palabras[:60],
        'clusters': clusters,
        'tendencias': tendencias,
        'territorio': territorio,
        'comparativas': comparativas,
        'predicciones': predicciones,
        'resumen': {
            'total_palabras_unicas': len(palabras),
            'total_clusters': len(clusters),
            'total_tendencias': len(tendencias),
            'departamentos_activos': len(territorio),
        },
    }


def _extraer_palabras() -> list[dict]:
    propuestas = Participacion.query.with_entities(Participacion.propuesta).all()
    textos = [p[0] for p in propuestas if p[0]]

    palabras = []
    for texto in textos:
        texto_limpio = re.sub(r'[^\w\sáéíóúñÁÉÍÓÚÑ]', ' ', texto.lower())
        tokens = texto_limpio.split()
        tokens_filtrados = [t for t in tokens if len(t) > 3 and t not in STOP_WORDS]
        palabras.extend(tokens_filtrados)

    contador = Counter(palabras)
    return [
        {'texto': palabra, 'frecuencia': frecuencia}
        for palabra, frecuencia in contador.most_common(100)
    ]


CLUSTER_KEYWORDS: dict[str, list[str]] = {
    'Infraestructura y servicios': [
        'vía', 'carretera', 'puente', 'acueducto', 'alcantarillado', 'energía',
        'agua', 'transporte', 'movilidad', 'vivienda', 'infraestructura',
    ],
    'Educación y juventud': [
        'educación', 'escuela', 'colegio', 'universidad', 'estudiante', 'docente',
        'joven', 'jóvenes', 'beca', 'formación', 'matrícula', 'aprendizaje',
    ],
    'Salud y bienestar': [
        'salud', 'hospital', 'médico', 'medicamento', 'eps', 'enfermedad',
        'bienestar', 'salud mental', 'discapacidad', 'adulto mayor',
    ],
    'Empleo y economía': [
        'empleo', 'trabajo', 'desempleo', 'empresa', 'emprendimiento', 'economía',
        'salario', 'ingreso', 'industria', 'comercio', 'turismo',
    ],
    'Seguridad y convivencia': [
        'seguridad', 'violencia', 'delincuencia', 'policía', 'inseguridad',
        'crimen', 'conflicto', 'paz', 'protección',
    ],
    'Ambiente y sostenibilidad': [
        'ambiente', 'ambiental', 'cambio climático', 'contaminación', 'reciclaje',
        'bosque', 'reforestación', 'residuos', 'agua', 'energía renovable',
    ],
}


def _generar_clusters() -> list[dict]:
    propuestas = Participacion.query.with_entities(
        Participacion.propuesta, Participacion.sector_prioritario_id
    ).all()

    cluster_counts = defaultdict(lambda: {'participaciones': 0, 'palabras_encontradas': set()})

    for propuesta, sector_id in propuestas:
        if not propuesta:
            continue
        texto = propuesta.lower()

        for cluster_nombre, keywords in CLUSTER_KEYWORDS.items():
            for kw in keywords:
                if kw in texto:
                    cluster_counts[cluster_nombre]['participaciones'] += 1
                    cluster_counts[cluster_nombre]['palabras_encontradas'].add(kw)
                    break

    result = []
    for nombre, datos in sorted(
        cluster_counts.items(),
        key=lambda x: x[1]['participaciones'],
        reverse=True,
    ):
        result.append({
            'nombre': nombre,
            'participaciones': datos['participaciones'],
            'palabras_clave': list(datos['palabras_encontradas'])[:5],
        })

    return result


def _tendencia_mensual() -> list[dict]:
    try:
        rows = (
            db.session.query(
                func.to_char(Participacion.created_at, 'YYYY-MM'),
                func.count(Participacion.id),
            )
            .group_by(func.to_char(Participacion.created_at, 'YYYY-MM'))
            .order_by(func.to_char(Participacion.created_at, 'YYYY-MM'))
            .all()
        )
    except Exception:
        rows = (
            db.session.query(
                func.date_trunc('month', Participacion.created_at),
                func.count(Participacion.id),
            )
            .group_by(func.date_trunc('month', Participacion.created_at))
            .order_by(func.date_trunc('month', Participacion.created_at))
            .all()
        )
    return [{'mes': str(mes)[:7], 'participaciones': total} for mes, total in rows]


DEPARTAMENTOS_COL: list[str] = [
    'Amazonas', 'Antioquia', 'Arauca', 'Atlántico', 'Bolívar', 'Boyacá',
    'Caldas', 'Caquetá', 'Casanare', 'Cauca', 'Cesar', 'Chocó',
    'Córdoba', 'Cundinamarca', 'Guainía', 'Guaviare', 'Huila',
    'La Guajira', 'Magdalena', 'Meta', 'Nariño', 'Norte de Santander',
    'Putumayo', 'Quindío', 'Risaralda', 'Santander', 'Sucre', 'Tolima',
    'Valle del Cauca', 'Vaupés', 'Vichada', 'Bogotá D.C.',
]

REGIONES: dict[str, list[str]] = {
    'Caribe': ['Atlántico', 'Bolívar', 'Cesar', 'Córdoba', 'La Guajira', 'Magdalena', 'Sucre'],
    'Pacífico': ['Cauca', 'Chocó', 'Nariño', 'Valle del Cauca'],
    'Andina': ['Antioquia', 'Boyacá', 'Caldas', 'Cundinamarca', 'Huila', 'Norte de Santander',
               'Quindío', 'Risaralda', 'Santander', 'Tolima'],
    'Orinoquía': ['Arauca', 'Casanare', 'Meta', 'Vichada'],
    'Amazonía': ['Amazonas', 'Caquetá', 'Guainía', 'Guaviare', 'Putumayo', 'Vaupés'],
    'Bogotá': ['Bogotá D.C.'],
}


def _analisis_territorial() -> list[dict]:
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
    depto_dict = dict(rows)

    region_counts = defaultdict(int)
    region_deptos = defaultdict(list)

    for depto in DEPARTAMENTOS_COL:
        total = depto_dict.get(depto, 0)
        for region, deptos in REGIONES.items():
            if depto in deptos:
                region_counts[region] += total
                if total > 0:
                    region_deptos[region].append({'nombre': depto, 'participaciones': total})
                break

    result = []
    for region, total in sorted(region_counts.items(), key=lambda x: x[1], reverse=True):
        result.append({
            'region': region,
            'total': total,
            'departamentos': region_deptos.get(region, []),
        })

    return result


def _comparativas_sector() -> dict[str, Any]:
    participaciones_por_sector = (
        db.session.query(Sector.nombre, func.count(Participacion.id))
        .join(Participacion.sectores)
        .group_by(Sector.nombre)
        .order_by(func.count(Participacion.id).desc())
        .all()
    )

    politicas_por_sector = defaultdict(int)
    for p in Politica.query.filter_by(activo=True).all():
        if p.sector:
            politicas_por_sector[p.sector.nombre] += 1

    sector_max = max(
        (s for s in participaciones_por_sector),
        key=lambda x: x[1],
        default=('N/A', 0),
    )
    depto_max_rows = (
        db.session.query(
            Participacion.departamento, func.count(Participacion.id)
        )
        .filter(
            Participacion.departamento.isnot(None),
            Participacion.departamento != '',
        )
        .group_by(Participacion.departamento)
        .order_by(func.count(Participacion.id).desc())
        .limit(1)
        .all()
    )
    depto_max = depto_max_rows[0][0] if depto_max_rows else 'N/A'

    return {
        'sector_lider': {'nombre': sector_max[0], 'total': sector_max[1]},
        'departamento_lider': depto_max,
        'total_sectores': len(participaciones_por_sector),
        'sectores_sin_politica': [
            nombre for nombre, _ in participaciones_por_sector
            if nombre not in politicas_por_sector
        ],
        'sectores': [
            {'nombre': nombre, 'participaciones': total, 'politicas': politicas_por_sector.get(nombre, 0)}
            for nombre, total in participaciones_por_sector
        ],
    }


def _predicciones() -> dict[str, Any]:
    tendencia = _tendencia_mensual()
    if not tendencia:
        return {'proyeccion_tendencia': 'creciente', 'estimado_proximo_mes': 0, 'confianza': 'baja'}

    totales = [t['participaciones'] for t in tendencia]
    if len(totales) >= 2:
        pendiente = (totales[-1] - totales[0]) / max(len(totales) - 1, 1)
    else:
        pendiente = 0

    if pendiente > 0.5:
        tendencia_label = 'creciente'
        confianza = 'alta'
    elif pendiente < -0.5:
        tendencia_label = 'decreciente'
        confianza = 'alta'
    else:
        tendencia_label = 'estable'
        confianza = 'media'

    promedio = sum(totales) / max(len(totales), 1)
    estimado = max(0, int(promedio + pendiente * 2))

    return {
        'proyeccion_tendencia': tendencia_label,
        'estimado_proximo_mes': estimado,
        'confianza': confianza,
        'datos_historicos': tendencia,
    }
