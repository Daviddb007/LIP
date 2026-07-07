from __future__ import annotations

import logging

from app import db
from app.models.sector import Sector
from app.models.problema import Problema
from app.models.politica import Politica

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


POLITICAS: list[dict] = [
    {
        'titulo': 'Familias en Acción',
        'sector_nombre': 'Economía y empleo',
        'resumen_ejecutivo': 'Programa de transferencias monetarias condicionadas del Gobierno Nacional que entrega subsidios a familias en situación de pobreza y vulnerabilidad, a cambio del cumplimiento de corresponsabilidades en salud y educación de sus hijos.',
        'problema': 'Colombia enfrenta altos niveles de pobreza monetaria y multidimensional, especialmente en zonas rurales y urbanas marginadas. Muchas familias no tienen ingresos suficientes para cubrir necesidades básicas y los niños abandonan la escuela por falta de recursos.',
        'objetivos': 'Reducir la pobreza y la desigualdad en hogares vulnerables; Fomentar la inversión en capital humano mediante corresponsabilidades en salud y educación; Romper la transmisión intergeneracional de la pobreza',
        'poblacion_objetivo': 'Familias en situación de pobreza y vulnerabilidad con niños, niñas y adolescentes menores de 18 años',
        'normatividad': 'CONPES Social; Ley 1532 de 2012; Decreto Reglamentario',
        'cronologia': '2001: Creación del programa Familias en Acción; 2007: Se integra a la Red Juntos; 2012: Se expide la Ley 1532 que lo formaliza; 2022: Se fusiona con Ingreso Solidario; 2026: Más de 4 millones de familias beneficiadas',
        'entidades_responsables': 'Departamento para la Prosperidad Social (DPS); Ministerio de Salud y Protección Social; Ministerio de Educación Nacional',
        'indicadores': 'Cobertura: 4 millones de familias; Tasa de escolaridad: 15% de aumento en zonas rurales; Controles de salud: 90% de cumplimiento',
        'presupuesto': '$3.5 billones anuales',
        'estado': 'Activa',
        'ods_relacionados': '1, 2, 3, 4, 10',
        'alcance': 'Nacional',
        'documentos': 'Ley 1532 de 2012; CONPES 3798; Informe de resultados DPS 2025',
    },
    {
        'titulo': 'Política Nacional de Cambio Climático',
        'sector_nombre': 'Medio ambiente',
        'resumen_ejecutivo': 'Estrategia nacional que busca reducir las emisiones de gases de efecto invernadero y adaptar al país a los efectos del cambio climático, con metas concretas a 2030 y 2050, integrando la variable climática en la planeación territorial y sectorial.',
        'problema': 'Colombia es uno de los países más vulnerables al cambio climático debido a su ubicación geográfica y características socioeconómicas. Fenómenos como inundaciones, sequías y deslizamientos afectan cada año a miles de colombianos y generan pérdidas económicas significativas.',
        'objetivos': 'Reducir las emisiones de GEI en un 51% para 2030; Alcanzar la carbono neutralidad a 2050; Integrar el cambio climático en la planeación de 32 departamentos; Fortalecer la capacidad de adaptación de comunidades vulnerables',
        'poblacion_objetivo': 'Toda la población colombiana, con énfasis en comunidades vulnerables al cambio climático',
        'normatividad': 'Ley 1931 de 2018 (Ley de Cambio Climático); CONPES 3700; CONPES 4023; NDC Actualizada 2020',
        'cronologia': '2015: Colombia firma el Acuerdo de París; 2018: Se expide la Ley 1931 de Cambio Climático; 2020: Se actualiza la NDC con metas más ambiciosas; 2022: Se adopta la Estrategia Climática de Largo Plazo (E2050); 2025: Reporte de avance: 30% de reducción de emisiones',
        'entidades_responsables': 'Ministerio de Ambiente y Desarrollo Sostenible; IDEAM; Corporaciones Autónomas Regionales; Gobernaciones y Alcaldías',
        'indicadores': 'Reducción de emisiones: 30% a 2025; Departamentos con planes de cambio climático: 32/32; Inversión en adaptación: $2 billones',
        'presupuesto': '$4 billones (públicos y privados)',
        'estado': 'Activa',
        'ods_relacionados': '7, 11, 12, 13, 14, 15',
        'alcance': 'Nacional',
        'documentos': 'Ley 1931 de 2018; CONPES 4023; NDC Colombia 2020; E2050',
    },
    {
        'titulo': 'Jornada Única Escolar',
        'sector_nombre': 'Educación',
        'resumen_ejecutivo': 'Política educativa que amplía el tiempo de permanencia de los estudiantes en instituciones educativas oficiales, pasando de media jornada (4 horas) a jornada completa (7 horas), para mejorar la calidad educativa y reducir la exposición a riesgos sociales.',
        'problema': 'La mayoría de instituciones educativas públicas en Colombia operaban con jornadas de media jornada (4 horas), lo que limitaba el tiempo de aprendizaje y exponía a los estudiantes a riesgos sociales en las horas no escolarizadas.',
        'objetivos': 'Ampliar la jornada escolar a 7 horas diarias en instituciones oficiales; Mejorar la calidad educativa mediante más tiempo de aprendizaje; Reducir la exposición de niños y jóvenes a riesgos sociales; Fortalecer actividades extracurriculares (deporte, cultura, tecnología)',
        'poblacion_objetivo': 'Estudiantes de instituciones educativas oficiales en todo el territorio nacional',
        'normatividad': 'Ley 1753 de 2015 (PND); Decreto 501 de 2016; Directiva Ministerial 05 de 2016',
        'cronologia': '2015: Se incluye en el Plan Nacional de Desarrollo; 2016: Se expide el Decreto que reglamenta la Jornada Única; 2018: 1.000 sedes educativas implementan la jornada única; 2022: Se amplía la cobertura a zonas rurales; 2025: Más de 50.000 estudiantes beneficiados',
        'entidades_responsables': 'Ministerio de Educación Nacional; Secretarías de Educación Departamentales y Municipales; Entidades Territoriales Certificadas',
        'indicadores': 'Estudiantes beneficiados: 50.000+; Sedes educativas: 1.000+; Horas de jornada: 7 horas diarias',
        'presupuesto': '$800.000 millones anuales',
        'estado': 'En formulación',
        'ods_relacionados': '4, 10',
        'alcance': 'Nacional',
        'documentos': 'Ley 1753 de 2015; Decreto 501 de 2016; Informe MEN de implementación',
    },
    {
        'titulo': 'Mi Casa Ya',
        'sector_nombre': 'Infraestructura',
        'resumen_ejecutivo': 'Programa de subsidios del Gobierno Nacional que facilita la compra de vivienda nueva a hogares de ingresos bajos y medios, mediante un subsidio a la cuota inicial y una cobertura a la tasa de interés del crédito hipotecario.',
        'problema': 'Déficit habitacional cuantitativo y cualitativo que afecta a millones de colombianos. Los hogares de bajos ingresos no pueden acceder a vivienda formal por falta de ahorro para la cuota inicial y altas tasas de interés hipotecario.',
        'objetivos': 'Facilitar el acceso a vivienda nueva a hogares de ingresos bajos y medios; Reducir el déficit habitacional; Dinamizar el sector de la construcción; Generar empleo en el sector',
        'poblacion_objetivo': 'Hogares con ingresos hasta 4 SMMLV que no sean propietarios de vivienda',
        'normatividad': 'Ley 1537 de 2012; Decreto 1259 de 2023; Resolución MVCT',
        'cronologia': '2015: Se crea el programa Mi Casa Ya; 2018: Se amplía el subsidio a hogares de ingresos medios; 2022: Se incrementa el valor del subsidio; 2024: Más de 300.000 hogares beneficiados; 2026: Nuevas condiciones y montos actualizados',
        'entidades_responsables': 'Ministerio de Vivienda, Ciudad y Territorio; Fondo Nacional de Vivienda (Fonvivienda); Entidades financieras',
        'indicadores': 'Hogares beneficiados: 300.000+; Subsidio máximo: $30 millones; Cobertura de tasa: hasta 5 puntos porcentuales',
        'presupuesto': '$1.5 billones anuales',
        'estado': 'Activa',
        'ods_relacionados': '1, 8, 11',
        'alcance': 'Nacional',
        'documentos': 'Ley 1537 de 2012; Decreto 1259 de 2023; Reglamento operativo Fonvivienda',
    },
    {
        'titulo': 'Política Nacional de Salud Mental',
        'sector_nombre': 'Salud',
        'resumen_ejecutivo': 'Estrategia integral del Gobierno Nacional para promover la salud mental, prevenir los trastornos mentales y garantizar la atención oportuna y de calidad a las personas que enfrentan problemas de salud mental en Colombia.',
        'problema': 'La salud mental en Colombia ha sido históricamente subpriorizada. La prevalencia de trastornos mentales es alta (depresión, ansiedad, suicidio) y los servicios de atención son insuficientes, especialmente en zonas rurales. La pandemia agravó esta situación.',
        'objetivos': 'Reducir la prevalencia de trastornos mentales en la población colombiana; Fortalecer la red de servicios de salud mental; Prevenir el suicidio y las conductas autolesivas; Promover el bienestar emocional desde la infancia; Integrar la salud mental en todos los niveles de atención',
        'poblacion_objetivo': 'Toda la población colombiana, con énfasis en niños, adolescentes, adultos mayores y víctimas del conflicto',
        'normatividad': 'Ley 1616 de 2013 (Ley de Salud Mental); CONPES 3992; Resolución 518 de 2015',
        'cronologia': '2013: Se expide la Ley 1616 de Salud Mental; 2015: Se adopta la Política Nacional de Salud Mental; 2018: Se crea el programa de prevención del suicidio; 2022: Se fortalecen los servicios comunitarios de salud mental; 2025: Se amplía la cobertura a 1.000 municipios',
        'entidades_responsables': 'Ministerio de Salud y Protección Social; EPS e IPS; Secretarías de Salud Departamentales y Municipales; ICBF',
        'indicadores': 'Cobertura de servicios: 1.000 municipios; Línea de atención: 24/7; Psicólogos por cada 10.000 hab: 15',
        'presupuesto': '$1.2 billones anuales',
        'estado': 'Activa',
        'ods_relacionados': '3, 10, 16',
        'alcance': 'Nacional',
        'documentos': 'Ley 1616 de 2013; CONPES 3992; Lineamientos técnicos MSPS',
    },
    {
        'titulo': 'Estrategia de Gobierno Digital',
        'sector_nombre': 'Tecnología',
        'resumen_ejecutivo': 'Política del Gobierno Nacional para transformar la administración pública mediante la digitalización de trámites, la interoperabilidad de sistemas y la prestación de servicios digitales centrados en el ciudadano.',
        'problema': 'Los ciudadanos enfrentan largas filas, trámites presenciales, duplicidad de información y baja eficiencia en la gestión pública. La brecha digital limita el acceso a servicios del Estado.',
        'objetivos': 'Digitalizar el 100% de los trámites de alta demanda; Implementar interoperabilidad entre entidades del Estado; Reducir tiempos y costos de trámites para los ciudadanos; Garantizar acceso inclusivo a servicios digitales',
        'poblacion_objetivo': 'Todos los ciudadanos colombianos que realizan trámites ante el Estado',
        'normatividad': 'Ley 1955 de 2019 (PND); Decreto 620 de 2020; CONPES 3975; Ley de TIC',
        'cronologia': '2018: Se formula la Política de Gobierno Digital; 2020: Se expide el Decreto 620 de Transformación Digital; 2021: Se lanza la plataforma GOV.CO; 2023: Más de 5.000 trámites digitalizados; 2025: Interoperabilidad entre 200 entidades',
        'entidades_responsables': 'Ministerio de Tecnologías de la Información y Comunicaciones (Mintic); Departamento Administrativo de la Función Pública; Entidades del orden nacional y territorial',
        'indicadores': 'Trámites digitalizados: 5.000+; Entidades interoperables: 200+; Usuarios de GOV.CO: 10 millones',
        'presupuesto': '$500.000 millones anuales',
        'estado': 'Activa',
        'ods_relacionados': '9, 16, 17',
        'alcance': 'Nacional',
        'documentos': 'Decreto 620 de 2020; CONPES 3975; Manual de Gobierno Digital',
    },
]


def seed_database() -> None:
    """Populate the database with initial sectors and problems if empty."""

    if Sector.query.count() > 0:
        _seed_politicas()
        return

    _seed_sectores()
    _seed_problemas()
    _seed_politicas()
    logger.info('Base de datos inicializada con sectores, problemas y políticas.')


def _seed_politicas() -> None:
    if Politica.query.count() > 0:
        return

    for p in POLITICAS:
        sector = Sector.query.filter_by(nombre=p.pop('sector_nombre')).first()
        politica = Politica(**p, sector_id=sector.id if sector else None)
        db.session.add(politica)

    db.session.commit()
    logger.info(f'Base de datos inicializada con {len(POLITICAS)} políticas.')


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
