"""
Diccionario de keywords para el motor SRIE v2.

Estructura: cada pilar tiene una lista de keywords con pesos (0.0-1.0).
Palabras en minúsculas, normalizadas (sin tildes).

Pesos:
  0.9-1.0 = keyword fuerte, casi garantiza el pilar
  0.6-0.8 = keyword moderado, contribuye significativamente
  0.3-0.5 = keyword débil, contribuye parcialmente
  0.1-0.2 = keyword contextual, contribuye poco
"""
from __future__ import annotations

# {pilar_slug: [(keyword, peso), ...]}
# Usamos pilar_slug para mapear después al pilar real

KEYWORDS_PILARES: dict[str, list[tuple[str, float]]] = {
    # Pilar Democrático (orden 1)
    "pilar-democratico": [
        ("constitucion", 1.0), ("constituyente", 0.9), ("democracia", 0.8),
        ("voto", 0.7), ("elecciones", 0.7), ("partido", 0.6),
        ("libertad", 0.7), ("derechos", 0.6), ("civico", 0.8),
        ("patriotismo", 0.9), ("constitucional", 1.0), ("debido proceso", 0.7),
        ("garantias", 0.6), ("participacion ciudadana", 0.8), ("rendicion", 0.6),
    ],
    # Iluminar la Patria (orden 2) - energía, tecnología
    "iluminar-la-patria": [
        ("energia", 0.9), ("electricidad", 0.8), ("solar", 0.7), ("eolica", 0.7),
        ("renovable", 0.8), ("tecnologia", 0.6), ("internet", 0.5),
        ("digital", 0.5), ("fibra optica", 0.7), ("banda ancha", 0.6),
        ("panel", 0.6), ("transmision", 0.7), ("subestacion", 0.8),
        ("lluminacion", 0.9), ("alumbrado", 0.7),
    ],
    # Defender la Patria (orden 3) - defensa, fronteras
    "defender-la-patria": [
        ("militar", 0.9), ("fuerzas armadas", 1.0), ("defensa", 0.8),
        ("frontera", 0.9), ("soberania", 0.8), ("guerrilla", 0.7),
        ("conflicto armado", 0.8), ("desminado", 0.9), ("victimas", 0.6),
        ("paz", 0.5), ("seguridad", 0.4), ("policia", 0.6),
    ],
    # Extrema Coherencia (orden 4) - coherencia política, meritocracia
    "extrema-coherencia": [
        ("coherencia", 1.0), ("meritocracia", 0.9), ("competencia", 0.7),
        ("profesionalismo", 0.8), ("tecnico", 0.6), ("ministro", 0.7),
        ("funcionario", 0.6), ("gestion", 0.5), ("planeacion", 0.6),
        ("efficiencia", 0.8), ("ahorro", 0.5), ("gasto publico", 0.7),
    ],
    # Seguridad (orden 5)
    "seguridad": [
        ("seguridad", 1.0), ("inseguridad", 0.9), ("robo", 0.9), ("hurto", 0.9),
        ("extorsion", 0.9), ("sicariato", 0.9), ("secuestro", 0.9),
        ("violencia", 0.8), ("crimen", 0.8), ("delincuencia", 0.9),
        ("barrio", 0.5), ("comuna", 0.5), ("policia", 0.7),
        ("fuerza publica", 0.8), ("cctv", 0.6), ("camara", 0.5),
        ("patrulla", 0.7), ("denuncia", 0.6), ("impunidad", 0.7),
        ("carcel", 0.5), ("penitenciaria", 0.6), ("mega carcel", 0.8),
        ("mega carceles", 0.8), ("droga", 0.7), ("narcotrafico", 0.8),
        ("microtrafico", 0.8), ("armas", 0.7), ("homicidio", 0.8),
        ("femicidio", 0.7),
    ],
    # Erradicar la Corrupción (orden 6)
    "erradicar-la-corrupcion": [
        ("corrupcion", 1.0), ("corrupto", 0.9), ("desfalco", 0.9),
        ("malversacion", 0.9), ("peculado", 0.9), ("cohecho", 0.9),
        ("clientelismo", 0.9), ("mordida", 0.8), ("soborno", 0.9),
        ("contratacion", 0.7), ("obra publica", 0.8), ("contrato", 0.6),
        ("transparencia", 0.8), ("rendicion", 0.7), ("fiscalia", 0.7),
        ("procuraduria", 0.7), ("contraloria", 0.7), ("lavado", 0.7),
        ("enriquecimiento", 0.6), ("patrimonio", 0.6), ("donaciones", 0.5),
        ("impuestos", 0.5), (" evasion", 0.6), ("buho", 0.4),
    ],
    # Recuperar la Salud (orden 7)
    "recuperar-la-salud": [
        ("salud", 1.0), ("hospital", 0.9), ("clinica", 0.8), ("ips", 0.9),
        ("medico", 0.8), ("enfermera", 0.8), ("eps", 0.9),
        ("medicamentos", 0.9), ("farmacia", 0.7), ("tratamiento", 0.7),
        ("diagnostico", 0.7), ("ambulancia", 0.8), ("urgencias", 0.8),
        ("cirugia", 0.7), ("especialista", 0.7), ("cita", 0.6),
        ("lista de espera", 0.8), ("consulta", 0.6), ("atencion", 0.6),
        ("seguro", 0.5), ("afiliacion", 0.6), ("contributivo", 0.6),
        ("subsidado", 0.6), ("sistema de salud", 0.8), ("pyp", 0.5),
        ("vacuna", 0.7), ("dengue", 0.6), ("malaria", 0.6),
        ("enfermedad", 0.7), ("cancer", 0.6), ("diabetes", 0.6),
        ("hipertension", 0.6), ("mental", 0.7), ("psicologia", 0.7),
        ("ansiedad", 0.7), ("depresion", 0.7), ("desnutricion", 0.8),
        ("nutricion", 0.7),
    ],
    # Campo y el Agro (orden 8)
    "campo-y-el-agro": [
        ("agro", 1.0), ("campo", 0.9), ("agricultura", 1.0), ("agricola", 0.9),
        ("campesino", 0.9), ("finca", 0.8), ("cosecha", 0.8), ("siembra", 0.8),
        ("tierra", 0.8), ("reforma", 0.7), ("predio", 0.7), ("parcela", 0.7),
        ("ganaderia", 0.8), ("ganado", 0.7), ("leche", 0.6),
        ("cafe", 0.7), ("ca panela", 0.6), ("cacao", 0.7), ("arroz", 0.7),
        ("maiz", 0.6), ("papa", 0.6), ("yuca", 0.6), ("platano", 0.6),
        ("fruta", 0.6), ("hortaliza", 0.6), ("apicultura", 0.7),
        ("rural", 0.7), ("vereda", 0.7), ("corregimiento", 0.6),
        ("productor", 0.7), ("asociacion", 0.5), ("cooperativa", 0.6),
        ("precio", 0.6), ("mercado", 0.5), ("comercializacion", 0.7),
        ("exportacion", 0.6), ("tecnologia agricola", 0.7), ("maquinaria", 0.6),
        ("riego", 0.8), ("agua", 0.5), ("sequia", 0.7),
        ("plaga", 0.6), ("cosecha", 0.6),
    ],
    # Patria para las Mujeres (orden 9)
    "patria-para-las-mujeres": [
        ("mujer", 1.0), ("mujeres", 0.9), ("genero", 0.8), ("femenino", 0.7),
        ("violencia de genero", 1.0), ("femicidio", 0.9), ("machismo", 0.8),
        ("brecha salarial", 0.9), ("equidad", 0.8), ("igualdad", 0.7),
        ("empoderamiento", 0.7), ("liderazgo femenino", 0.8),
        ("trabajo domestico", 0.7), ("cuidado", 0.6), ("maternidad", 0.7),
        ("reproductivo", 0.6), ("salud sexual", 0.7), ("planificacion", 0.6),
        ("aborto", 0.5), ("acoso", 0.8), ("hostigamiento", 0.8),
        ("discriminacion", 0.7), ("techo proprio", 0.6),
    ],
    # Minero-Energético (orden 10)
    "minero-energetico": [
        ("mineria", 1.0), ("minero", 0.9), ("petroleo", 0.9), ("gas", 0.7),
        ("energia", 0.8), ("carbon", 0.8), ("oro", 0.7), ("esmeralda", 0.7),
        ("emergente", 0.6), ("industria", 0.7), ("manufactura", 0.7),
        ("empresa", 0.6), ("empleo", 0.8), ("trabajo", 0.6),
        ("formal", 0.5), ("economico", 0.5), ("crecimiento", 0.5),
        ("pib", 0.5), ("inversion", 0.6), ("desarrollo", 0.5),
        ("infraestructura", 0.6), ("vial", 0.5), ("transporte", 0.6),
        ("puerto", 0.6), ("aeropuerto", 0.6), ("ferrocarril", 0.7),
        ("vivienda", 0.5), ("acueducto", 0.6), ("saneamiento", 0.6),
        ("internet", 0.5), ("conectividad", 0.5), ("tecnologia", 0.5),
    ],
    # Educación (orden 11)
    "educacion": [
        ("educacion", 1.0), ("escolar", 0.9), ("colegio", 0.9), ("universidad", 0.8),
        ("docente", 0.9), ("profesor", 0.9), ("estudiante", 0.8), ("alumno", 0.8),
        ("enseñanza", 0.9), ("aprendizaje", 0.8), ("aula", 0.8), ("matricula", 0.7),
        ("beca", 0.7), ("pensión", 0.6), ("calidad", 0.6), ("cobertura", 0.6),
        ("desercion", 0.8), ("repetencia", 0.7), ("analfabetismo", 0.9),
        ("biblioteca", 0.7), ("laboratorio", 0.7), ("tecnico", 0.6),
        ("tecnologico", 0.6), ("sena", 0.7), ("formacion", 0.6),
        ("investigacion", 0.6), ("ciencia", 0.6), ("pensamiento", 0.5),
        ("lectura", 0.6), ("escritura", 0.5), ("matematicas", 0.6),
        ("ingles", 0.5), ("competencias", 0.5),
    ],
    # Cultura (orden 12)
    "cultura": [
        ("cultura", 1.0), ("artistico", 0.9), ("musica", 0.8), ("teatro", 0.8),
        ("danza", 0.7), ("pintura", 0.7), ("escultura", 0.7), ("literatura", 0.7),
        ("cine", 0.7), ("patrimonio", 0.8), ("tradiccion", 0.7), ("folclor", 0.8),
        ("identidad", 0.6), ("creatividad", 0.7), ("industria cultural", 0.9),
        ("artesania", 0.8), ("turismo", 0.6), ("fiesta", 0.5),
        ("carnaval", 0.6), ("colombiamarca", 0.5),
    ],
    # Proteger el Medioambiente (orden 13)
    "proteger-el-medioambiente": [
        ("medioambiente", 1.0), ("medio ambiente", 1.0), ("ambiental", 0.9),
        ("deforestacion", 0.9), ("bosque", 0.8), ("selva", 0.7),
        ("contaminacion", 0.9), ("contaminado", 0.8), ("reciclaje", 0.7),
        ("residuo", 0.7), ("basura", 0.7), ("vertimiento", 0.8),
        ("rio", 0.7), ("quebrada", 0.7), ("humedal", 0.8),
        ("especie", 0.7), ("fauna", 0.7), ("flora", 0.7), ("biodiversidad", 0.8),
        ("cambio climatico", 0.9), ("clima", 0.6), ("temperatura", 0.5),
        ("sequia", 0.7), ("inundacion", 0.7), ("desastre", 0.6),
        ("amazonia", 0.7), ("pacifico", 0.6), ("paramo", 0.8),
        ("humedal", 0.8), ("aire", 0.6), ("aire limpio", 0.7),
    ],
    # Bienestar Animal (orden 14)
    "bienestar-animal-integral": [
        ("animal", 1.0), ("mascota", 0.9), ("perro", 0.8), ("gato", 0.8),
        ("maltrato animal", 1.0), ("abuso animal", 0.9), ("vet", 0.7),
        ("veterinaria", 0.7), ("adiestramiento", 0.6), ("adopcion", 0.8),
        ("refugio", 0.7), ("protectores", 0.8), ("bienestar animal", 1.0),
        ("zoonosis", 0.7), ("rabia", 0.6), ("esterilizacion", 0.7),
        ("leishmaniasis", 0.7), ("fauna", 0.6), ("salud publica", 0.5),
    ],
    # Megacárceles (orden 15)
    "megacarceles-y-megacentros": [
        ("carcel", 0.9), ("carceles", 0.9), ("mega carcel", 1.0),
        ("mega carceles", 1.0), ("penitenciaria", 0.9), ("reclusion", 0.8),
        ("preso", 0.8), ("interno", 0.7), ("sentenciado", 0.7),
        ("hacinamiento", 0.9), ("sobrepoblacion", 0.8), ("rehabilitacion", 0.8),
        ("reinsercion", 0.8), ("regreso", 0.6), ("trabajo penitenciario", 0.7),
        ("educacion penitenciaria", 0.7), ("mega centro", 0.9),
        ("megacentro", 0.9),
    ],
    # Defender la Constitución (orden 16)
    "defender-la-constitucion-de-1991": [
        ("constitucion", 1.0), ("constituyente", 0.9), ("1991", 0.9),
        ("constitucional", 0.9), ("derechos fundamentales", 0.8),
        ("sentencia", 0.7), ("corte", 0.6), ("tribunal", 0.6),
        ("jurisdiccion", 0.6), ("amparo", 0.7), ("tutela", 0.8),
        ("habeas corpus", 0.7), ("debido proceso", 0.7), ("autonomia", 0.6),
        ("descentralizacion", 0.7), ("regional", 0.5), ("gobernador", 0.6),
        ("alcalde", 0.6), ("orden publico", 0.5),
    ],
    # Jóvenes (orden 17)
    "los-jovenes": [
        ("joven", 1.0), ("jovenes", 0.9), ("adolescente", 0.8), ("adolescentes", 0.8),
        ("universitario", 0.7), ("estudiante", 0.6), ("emprendedor", 0.7),
        ("oportunidad", 0.7), ("futuro", 0.6), ("drogas", 0.7),
        ("adiccion", 0.7), ("consumo", 0.5), ("prevencion", 0.6),
        ("deporte", 0.6), ("recreacion", 0.6), ("cultura", 0.5),
        ("paz", 0.5), ("ciudadania", 0.6), ("liderazgo", 0.6),
        ("voluntariado", 0.6), ("pensión", 0.5), ("beca", 0.6),
        ("empleo", 0.5), ("desempleo", 0.6), ("informalidad", 0.5),
    ],
}

# Mapeo sector_slug → pilar_slug para boost
SECTOR_PILAR_BOOST: dict[str, str] = {
    "empleo-economia": "minero-energetico",
    "seguridad-convivencia": "seguridad",
    "salud-bienestar": "recuperar-la-salud",
    "educacion-cultura": "educacion",
    "gobierno-corrupcion": "erradicar-la-corrupcion",
    "campo-agro-medioambiente": "campo-y-el-agro",
    "infraestructura-servicios": "minero-energetico",
    "genero-juventud-comunidad": "patria-para-las-mujeres",
}

# Mapeo problema_slug → pilar_slug (del seed)
PROBLEMA_PILAR_SLUG_MAP: dict[str, str] = {
    "falta-empleo-formal": "minero-energetico",
    "desempleo-juvenil": "los-jovenes",
    "falta-capital-semilla": "minero-energetico",
    "tramites-formalizar": "minero-energetico",
    "impuestos-altos": "minero-energetico",
    "informalidad-laboral": "minero-energetico",
    "inseguridad-barrios": "seguridad",
    "robo-hurto": "seguridad",
    "extorsion": "seguridad",
    "violencia-mujer": "patria-para-las-mujeres",
    "maltrato-infantil": "patria-para-las-mujeres",
    "narcotrafico": "seguridad",
    "microtrafico": "seguridad",
    "falta-ips": "recuperar-la-salud",
    "listas-espera": "recuperar-la-salud",
    "falta-medicamentos": "recuperar-la-salud",
    "falta-atencion-psicologica": "recuperar-la-salud",
    "estres-laboral": "recuperar-la-salud",
    "inseguridad-alimentaria": "recuperar-la-salud",
    "desnutricion-infantil": "recuperar-la-salud",
    "baja-calidad-ensenanza": "educacion",
    "falta-docentes": "educacion",
    "desercion-escolar": "educacion",
    "colegios-deteriorados": "educacion",
    "falta-tecnologia": "educacion",
    "falta-bibliotecas": "cultura",
    "poca-oferta-cultural": "cultura",
    "obras-sin-ejecutar": "erradicar-la-corrupcion",
    "mal-uso-recursos": "erradicar-la-corrupcion",
    "desconexion-autoridades": "defender-la-constitucion-de-1991",
    "falta-rendicion-cuentas": "erradicar-la-corrupcion",
    "corrupcion-contratacion": "erradicar-la-corrupcion",
    "clientelismo": "erradicar-la-corrupcion",
    "falta-tierra": "campo-y-el-agro",
    "bajos-precios-campo": "campo-y-el-agro",
    "falta-asistencia-tecnica": "campo-y-el-agro",
    "violencia-rural": "seguridad",
    "desplazamiento-forzado": "seguridad",
    "deforestacion": "proteger-el-medioambiente",
    "contaminacion-aire": "proteger-el-medioambiente",
    "contaminacion-rios": "proteger-el-medioambiente",
    "falta-agua-potable": "campo-y-el-agro",
    "sequias-prolongadas": "campo-y-el-agro",
    "mal-estado-vias": "minero-energetico",
    "falta-transporte-publico": "minero-energetico",
    "falta-acueducto": "minero-energetico",
    "falta-alcantarillado": "minero-energetico",
    "deficit-vivienda": "minero-energetico",
    "viviendas-mal-estado": "minero-energetico",
    "falta-internet": "minero-energetico",
    "zonas-sin-cobertura": "minero-energetico",
    "brecha-salarial-genero": "patria-para-las-mujeres",
    "falta-equidad-laboral": "patria-para-las-mujeres",
    "falta-oportunidades-juveniles": "los-jovenes",
    "drogadiccion-juvenil": "los-jovenes",
    "abandono-adultos-mayores": "los-jovenes",
    "falta-pensiones": "los-jovenes",
}
