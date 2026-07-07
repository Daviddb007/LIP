from __future__ import annotations

import re

PILARES_ESTRATEGICOS: dict[str, dict] = {
    'Seguridad y Defensa': {
        'keywords': ['seguridad', 'defensa', 'conflicto', 'violencia', 'delincuencia', 'policía',
                     'ejército', 'paz', 'posconflicto', 'criminalidad', 'inseguridad', 'extorsión',
                     'sicariato', 'grupos armados', 'narcotráfico', 'minería ilegal'],
        'color': '#ef4444',
        'icono': 'shield-fill',
    },
    'Salud y Protección Social': {
        'keywords': ['salud', 'hospital', 'médico', 'EPS', 'medicamentos', 'vacunación',
                     'salud pública', 'protección social', 'seguridad social', 'bienestar',
                     'enfermedad', 'pandemia', 'salud mental', 'discapacidad', 'adulto mayor'],
        'color': '#10b981',
        'icono': 'heart-pulse-fill',
    },
    'Educación y Cultura': {
        'keywords': ['educación', 'escuela', 'colegio', 'universidad', 'docente', 'estudiante',
                     'cultura', 'deporte', 'analfabetismo', 'formación', 'becas', 'matrícula',
                     'deserción', 'infraestructura educativa', 'biblioteca'],
        'color': '#8b5cf6',
        'icono': 'book-fill',
    },
    'Infraestructura y Transporte': {
        'keywords': ['infraestructura', 'transporte', 'carretera', 'vía', 'puente', 'aeropuerto',
                     'puerto', 'movilidad', 'transporte público', 'metro', 'ferrocarril',
                     'mantenimiento vial', 'conectividad', 'malla vial'],
        'color': '#f59e0b',
        'icono': 'signpost-2-fill',
    },
    'Vivienda y Ciudad': {
        'keywords': ['vivienda', 'casa', 'barrio', 'urbanización', 'vivienda de interés social',
                     'subsidio', 'mejoramiento', 'asentamiento', 'vivienda rural', 'déficit',
                     'espacio público', 'servicios públicos', 'acueducto', 'alcantarillado'],
        'color': '#06b6d4',
        'icono': 'house-door-fill',
    },
    'Desarrollo Económico y Empleo': {
        'keywords': ['empleo', 'trabajo', 'economía', 'empresa', 'emprendimiento', 'industria',
                     'comercio', 'turismo', 'innovación', 'desempleo', 'formalización',
                     'microempresa', 'PYME', 'agricultura', 'campesino', 'minería'],
        'color': '#3b82f6',
        'icono': 'graph-up-arrow',
    },
    'Medio Ambiente y Sostenibilidad': {
        'keywords': ['medio ambiente', 'ambiente', 'sostenible', 'ecología', 'cambio climático',
                     'agua', 'río', 'bosque', 'conservación', 'contaminación', 'residuos',
                     'reciclaje', 'energía', 'energía renovable', 'minería ilegal',
                     'deforestación', 'animales', 'fauna', 'flora', 'parque natural'],
        'color': '#22c55e',
        'icono': 'tree-fill',
    },
    'Gobierno y Participación': {
        'keywords': ['gobierno', 'participación', 'corrupción', 'transparencia', 'justicia',
                     'democracia', 'derechos humanos', 'instituciones', 'estado', 'burocracia',
                     'rendición de cuentas', 'control social', 'veeduría', 'contratación'],
        'color': '#6366f1',
        'icono': 'building-fill',
    },
    'Tecnología e Innovación': {
        'keywords': ['tecnología', 'digital', 'internet', 'conectividad', 'innovación', 'software',
                     'datos', 'inteligencia artificial', 'transformación digital',
                     'gobierno digital', 'Brecha digital', 'TIC', 'aplicación', 'plataforma'],
        'color': '#ec4899',
        'icono': 'cpu-fill',
    },
    'Desarrollo Social y Equidad': {
        'keywords': ['pobreza', 'desigualdad', 'inclusión', 'equidad', 'vulnerable',
                     'discriminación', 'género', 'comunidad', 'indígena', 'afrocolombiano',
                     'desplazamiento', 'migración', 'hambre', 'nutrición', 'infancia',
                     'juventud', 'familia', 'LGBT', 'diversidad'],
        'color': '#f97316',
        'icono': 'hand-index-fill',
    },
}

NIVELES_URGENCIA: list[dict] = [
    {'nivel': 'Crítica', 'palabras': 5, 'color': '#dc2626', 'descripcion': 'Requiere atención inmediata'},
    {'nivel': 'Alta', 'palabras': 3, 'color': '#ea580c', 'descripcion': 'Debe abordarse en el corto plazo'},
    {'nivel': 'Moderada', 'palabras': 2, 'color': '#ca8a04', 'descripcion': 'Requiere planificación'},
    {'nivel': 'Baja', 'palabras': 0, 'color': '#16a34a', 'descripcion': 'Puede gestionarse a largo plazo'},
]

NIVELES_IMPACTO: list[dict] = [
    {'nivel': 'Nacional', 'color': '#7c3aed', 'descripcion': 'Afecta a todo el país'},
    {'nivel': 'Regional', 'color': '#2563eb', 'descripcion': 'Afecta a una región'},
    {'nivel': 'Local', 'color': '#059669', 'descripcion': 'Afecta a un municipio/comunidad'},
]


def clasificar(data: dict) -> dict:
    texto_completo = _combinar_texto(data)
    pilar = _detectar_pilar(texto_completo, data.get('sectores', []))
    urgencia = _calcular_urgencia(texto_completo, data)
    impacto = _estimar_impacto(data)
    explicacion = _generar_explicacion(pilar, urgencia, impacto, data)

    return {
        'pilar': pilar,
        'urgencia': urgencia,
        'impacto': impacto,
        'explicacion': explicacion,
    }


def _combinar_texto(data: dict) -> str:
    partes = [
        data.get('problema_principal', ''),
        data.get('propuesta', ''),
        data.get('contexto_ciudadano', ''),
    ]
    if data.get('propuestas'):
        for p in data['propuestas']:
            partes.append(p.get('propuesta', ''))
    return ' '.join(partes).lower()


def _detectar_pilar(texto: str, sectores_ids: list) -> dict:
    puntajes: dict[str, int] = {}

    for pilar, config in PILARES_ESTRATEGICOS.items():
        score = 0
        for keyword in config['keywords']:
            apariciones = len(re.findall(re.escape(keyword), texto))
            score += apariciones
        if score > 0:
            puntajes[pilar] = score

    if not puntajes:
        nombre_sector = _sector_nombre_por_id(sectores_ids[0]) if sectores_ids else 'General'
        for pilar in PILARES_ESTRATEGICOS:
            if nombre_sector.lower() in pilar.lower():
                puntajes[pilar] = 1

    if not puntajes:
        puntajes['Desarrollo Social y Equidad'] = 1

    pilar_principal = max(puntajes, key=puntajes.get)
    config = PILARES_ESTRATEGICOS[pilar_principal]

    return {
        'nombre': pilar_principal,
        'color': config['color'],
        'icono': config['icono'],
        'confianza': min(100, puntajes[pilar_principal] * 20),
    }


def _sector_nombre_por_id(sector_id: int) -> str:
    from app.models.sector import Sector
    sector = Sector.find_by_id(sector_id)
    return sector.nombre if sector else 'General'


def _calcular_urgencia(texto: str, data: dict) -> dict:
    palabras_urgencia = ['urgente', 'inmediato', 'grave', 'crítico', 'emergencia', 'alarma',
                         'prioridad', 'alta', 'riesgo', 'catástrofe', 'desastre', 'crisis',
                         'violento', 'muerte', 'enfermedad', 'hambre', 'desplazamiento',
                         'inundación', 'sequía', 'conflicto', 'desabastecimiento']

    conteo = sum(1 for palabra in palabras_urgencia if palabra in texto)

    for nivel in NIVELES_URGENCIA:
        if conteo >= nivel['palabras']:
            return {
                'nivel': nivel['nivel'],
                'color': nivel['color'],
                'descripcion': nivel['descripcion'],
            }

    return {
        'nivel': NIVELES_URGENCIA[-1]['nivel'],
        'color': NIVELES_URGENCIA[-1]['color'],
        'descripcion': NIVELES_URGENCIA[-1]['descripcion'],
    }


def _estimar_impacto(data: dict) -> dict:
    actores = data.get('actores_responsables', '').lower()
    beneficiarios = data.get('beneficiarios', '').lower()
    texto = f'{actores} {beneficiarios}'

    if any(p in texto for p in ['nación', 'nacional', 'todo el país', 'colombia', 'presidencia',
                                  'ministerio', 'congreso']):
        nivel = NIVELES_IMPACTO[0]
    elif any(p in texto for p in ['departamento', 'regional', 'gobernación', 'provincia']):
        nivel = NIVELES_IMPACTO[1]
    else:
        nivel = NIVELES_IMPACTO[2]

    return {
        'nivel': nivel['nivel'],
        'color': nivel['color'],
        'descripcion': nivel['descripcion'],
    }


def _generar_explicacion(pilar: dict, urgencia: dict, impacto: dict, data: dict) -> str:
    partes = [
        f"Tu participación ha sido clasificada dentro del pilar estratégico **{pilar['nombre']}** "
        f"con una confianza del {pilar['confianza']}%.",
        f"",
        f"El nivel de urgencia detectado es **{urgencia['nivel']}**: {urgencia['descripcion']}.",
        f"El alcance del impacto estimado es **{impacto['nivel']}**: {impacto['descripcion']}.",
        f"",
        f"Esta clasificación fue generada automáticamente por el motor **SRIE** (Sistema de "
        f"Recolección e Inteligencia Estratégica) de StoneLytics, analizando el contenido de "
        f"tu propuesta, el contexto y los sectores seleccionados.",
    ]

    return '\n'.join(partes)
