"""
Seed de datos V3: Plan estratégico + catálogos completos.

Plan: "El Milagro de los 'Nunca' — Primeros Pilares para Reconstruir la Patria Milagro"
Sectores: 8 sectores, ~25 subsectores, ~60 problemas
Actores: 10, Beneficiarios: 10
"""
from __future__ import annotations

import re
import unicodedata
from datetime import date

from app import db
from app.models.plan import Plan, Pilar, LineaEstrategica, Componente, Objetivo
from app.models.catalog import Sector, Subsector, ProblemaCatalogo, Actor, Beneficiario


# ---------------------------------------------------------------------
# 1. Plan
# ---------------------------------------------------------------------
PLAN_NOMBRE = "El Milagro de los 'Nunca' — Primeros Pilares para Reconstruir la Patria Milagro"

# ---------------------------------------------------------------------
# 2. Pilares
# ---------------------------------------------------------------------
PILARES: list[dict] = [
    {"orden": 0, "tipo": "fundacional", "nombre": "Movimiento Popular", "slug": "movimiento-popular"},
    {"orden": 1, "tipo": "fundacional", "nombre": "Pilar Democrático: los Defensores de la Patria", "slug": "pilar-democratico"},
    {"orden": 2, "tipo": "tematico", "nombre": "El Milagro de Iluminar la Patria", "slug": "iluminar-la-patria"},
    {"orden": 3, "tipo": "tematico", "nombre": "El Milagro de Defender la Patria para Salvarla", "slug": "defender-la-patria"},
    {"orden": 4, "tipo": "tematico", "nombre": "El Milagro de la Extrema Coherencia", "slug": "extrema-coherencia"},
    {"orden": 5, "tipo": "tematico", "nombre": "El Milagro de la Seguridad", "slug": "seguridad"},
    {"orden": 6, "tipo": "tematico", "nombre": "El Milagro de Erradicar la Corrupción", "slug": "erradicar-la-corrupcion"},
    {"orden": 7, "tipo": "tematico", "nombre": "El Milagro de Recuperar la Salud", "slug": "recuperar-la-salud"},
    {"orden": 8, "tipo": "tematico", "nombre": "El Milagro del Campo y el Agro", "slug": "campo-y-el-agro"},
    {"orden": 9, "tipo": "tematico", "nombre": "El Milagro de una Patria para las Mujeres", "slug": "patria-para-las-mujeres"},
    {"orden": 10, "tipo": "tematico", "nombre": "El Milagro Minero-Energético", "slug": "minero-energetico"},
    {"orden": 11, "tipo": "tematico", "nombre": "El Milagro de la Educación", "slug": "educacion"},
    {"orden": 12, "tipo": "tematico", "nombre": "El Milagro de la Cultura", "slug": "cultura"},
    {"orden": 13, "tipo": "tematico", "nombre": "El Milagro de Proteger el Medioambiente", "slug": "proteger-el-medioambiente"},
    {"orden": 14, "tipo": "tematico", "nombre": "El Milagro del Bienestar Animal Integral", "slug": "bienestar-animal-integral"},
    {"orden": 15, "tipo": "tematico", "nombre": "El Milagro de las Megacárceles y los Megacentros", "slug": "megacarceles-y-megacentros"},
    {"orden": 16, "tipo": "tematico", "nombre": "El Milagro de Defender la Constitución de 1991", "slug": "defender-la-constitucion-de-1991"},
    {"orden": 17, "tipo": "tematico", "nombre": "El Milagro de los Jóvenes", "slug": "los-jovenes"},
]

LINEAS_PILAR_DEMOCRATICO: list[str] = [
    "El Patriotismo Constitucional",
    "Un pilar para sostenerse contra la ofensiva constituyente",
    "Contrato de lealtad con la Constitución",
    "No más combinación de todas las formas de lucha",
    "El alcance de nuestra propuesta",
]

# ---------------------------------------------------------------------
# 3. Sectores (8)
# ---------------------------------------------------------------------
SECTORES: list[dict] = [
    {"nombre": "Empleo y Economía", "slug": "empleo-economia", "icono": "briefcase", "color": "#3B82F6", "orden": 1},
    {"nombre": "Seguridad y Convivencia", "slug": "seguridad-convivencia", "icono": "shield", "color": "#EF4444", "orden": 2},
    {"nombre": "Salud y Bienestar", "slug": "salud-bienestar", "icono": "heart", "color": "#10B981", "orden": 3},
    {"nombre": "Educación y Cultura", "slug": "educacion-cultura", "icono": "book", "color": "#8B5CF6", "orden": 4},
    {"nombre": "Gobierno y Corrupción", "slug": "gobierno-corrupcion", "icono": "building", "color": "#F59E0B", "orden": 5},
    {"nombre": "Campo, Agro y Medio Ambiente", "slug": "campo-agro-medioambiente", "icono": "tree", "color": "#22C55E", "orden": 6},
    {"nombre": "Infraestructura y Servicios", "slug": "infraestructura-servicios", "icono": "house", "color": "#06B6D4", "orden": 7},
    {"nombre": "Género, Juventud y Comunidad", "slug": "genero-juventud-comunidad", "icono": "people", "color": "#EC4899", "orden": 8},
]

# ---------------------------------------------------------------------
# 4. Subsectores (~25)
# ---------------------------------------------------------------------
SUBSECTORES: list[dict] = [
    # Empleo y Economía
    {"sector_slug": "empleo-economia", "nombre": "Generación de empleo", "slug": "generacion-empleo", "icono": "person-workspace", "orden": 1},
    {"sector_slug": "empleo-economia", "nombre": "Emprendimiento", "slug": "emprendimiento", "icono": "rocket", "orden": 2},
    {"sector_slug": "empleo-economia", "nombre": "Economía formal", "slug": "economia-formal", "icono": "cash", "orden": 3},
    # Seguridad y Convivencia
    {"sector_slug": "seguridad-convivencia", "nombre": "Seguridad ciudadana", "slug": "seguridad-ciudadana", "icono": "shield-lock", "orden": 1},
    {"sector_slug": "seguridad-convivencia", "nombre": "Violencia intrafamiliar", "slug": "violencia-intrafamiliar", "icono": "house-exclamation", "orden": 2},
    {"sector_slug": "seguridad-convivencia", "nombre": "Tráfico de drogas", "slug": "trafico-drogas", "icono": "exclamation-triangle", "orden": 3},
    # Salud y Bienestar
    {"sector_slug": "salud-bienestar", "nombre": "Acceso a salud", "slug": "acceso-salud", "icono": "hospital", "orden": 1},
    {"sector_slug": "salud-bienestar", "nombre": "Salud mental", "slug": "salud-mental", "icono": "brain", "orden": 2},
    {"sector_slug": "salud-bienestar", "nombre": "Nutrición", "slug": "nutricion", "icono": "egg", "orden": 3},
    # Educación y Cultura
    {"sector_slug": "educacion-cultura", "nombre": "Calidad educativa", "slug": "calidad-educativa", "icono": "mortarboard", "orden": 1},
    {"sector_slug": "educacion-cultura", "nombre": "Infraestructura educativa", "slug": "infraestructura-educativa", "icono": "building", "orden": 2},
    {"sector_slug": "educacion-cultura", "nombre": "Acceso cultural", "slug": "acceso-cultural", "icono": "palette", "orden": 3},
    # Gobierno y Corrupción
    {"sector_slug": "gobierno-corrupcion", "nombre": "Transparencia", "slug": "transparencia", "icono": "eye", "orden": 1},
    {"sector_slug": "gobierno-corrupcion", "nombre": "Participación ciudadana", "slug": "participacion-ciudadana", "icono": "chat-dots", "orden": 2},
    {"sector_slug": "gobierno-corrupcion", "nombre": "Contratación pública", "slug": "contratacion-publica", "icono": "file-earmark-text", "orden": 3},
    # Campo, Agro y Medio Ambiente
    {"sector_slug": "campo-agro-medioambiente", "nombre": "Agricultura", "slug": "agricultura", "icono": "crop", "orden": 1},
    {"sector_slug": "campo-agro-medioambiente", "nombre": "Reforma rural", "slug": "reforma-rural", "icono": "house-door", "orden": 2},
    {"sector_slug": "campo-agro-medioambiente", "nombre": "Protección ambiental", "slug": "proteccion-ambiental", "icono": "leaf", "orden": 3},
    {"sector_slug": "campo-agro-medioambiente", "nombre": "Recursos hídricos", "slug": "recursos-hidricos", "icono": "droplet", "orden": 4},
    # Infraestructura y Servicios
    {"sector_slug": "infraestructura-servicios", "nombre": "Vías y transporte", "slug": "vias-transporte", "icono": "road", "orden": 1},
    {"sector_slug": "infraestructura-servicios", "nombre": "Agua y saneamiento", "slug": "agua-saneamiento", "icono": "cup", "orden": 2},
    {"sector_slug": "infraestructura-servicios", "nombre": "Vivienda", "slug": "vivienda", "icono": "house-heart", "orden": 3},
    {"sector_slug": "infraestructura-servicios", "nombre": "Conectividad", "slug": "conectividad", "icono": "wifi", "orden": 4},
    # Género, Juventud y Comunidad
    {"sector_slug": "genero-juventud-comunidad", "nombre": "Equidad de género", "slug": "equidad-genero", "icono": "gender-female", "orden": 1},
    {"sector_slug": "genero-juventud-comunidad", "nombre": "Oportunidades juveniles", "slug": "oportunidades-juveniles", "icono": "emoji-laughing", "orden": 2},
    {"sector_slug": "genero-juventud-comunidad", "nombre": "Adultos mayores", "slug": "adultos-mayores", "icono": "person-standing", "orden": 3},
]

# ---------------------------------------------------------------------
# 5. Problemas (~60)
# ---------------------------------------------------------------------
PROBLEMAS_CATALOGO: list[dict] = [
    # Empleo y Economía → Generación de empleo
    {"subsector_slug": "generacion-empleo", "nombre": "Falta de empleo formal", "slug": "falta-empleo-formal", "icono": "x-circle", "orden": 1},
    {"subsector_slug": "generacion-empleo", "nombre": "Desempleo juvenil", "slug": "desempleo-juvenil", "icono": "x-circle", "orden": 2},
    # Empleo y Economía → Emprendimiento
    {"subsector_slug": "emprendimiento", "nombre": "Falta de capital semilla", "slug": "falta-capital-semilla", "icono": "x-circle", "orden": 1},
    {"subsector_slug": "emprendimiento", "nombre": "Trámites para formalizar", "slug": "tramites-formalizar", "icono": "x-circle", "orden": 2},
    # Empleo y Economía → Economía formal
    {"subsector_slug": "economia-formal", "nombre": "Impuestos altos", "slug": "impuestos-altos", "icono": "x-circle", "orden": 1},
    {"subsector_slug": "economia-formal", "nombre": "Informalidad laboral", "slug": "informalidad-laboral", "icono": "x-circle", "orden": 2},
    # Seguridad → Seguridad ciudadana
    {"subsector_slug": "seguridad-ciudadana", "nombre": "Inseguridad en barrios", "slug": "inseguridad-barrios", "icono": "x-circle", "orden": 1},
    {"subsector_slug": "seguridad-ciudadana", "nombre": "Robo y hurto", "slug": "robo-hurto", "icono": "x-circle", "orden": 2},
    {"subsector_slug": "seguridad-ciudadana", "nombre": "Extorsión", "slug": "extorsion", "icono": "x-circle", "orden": 3},
    # Seguridad → Violencia intrafamiliar
    {"subsector_slug": "violencia-intrafamiliar", "nombre": "Violencia contra la mujer", "slug": "violencia-mujer", "icono": "x-circle", "orden": 1},
    {"subsector_slug": "violencia-intrafamiliar", "nombre": "Maltrato infantil", "slug": "maltrato-infantil", "icono": "x-circle", "orden": 2},
    # Seguridad → Tráfico de drogas
    {"subsector_slug": "trafico-drogas", "nombre": "Narcotráfico", "slug": "narcotrafico", "icono": "x-circle", "orden": 1},
    {"subsector_slug": "trafico-drogas", "nombre": "Microtráfico", "slug": "microtrafico", "icono": "x-circle", "orden": 2},
    # Salud → Acceso a salud
    {"subsector_slug": "acceso-salud", "nombre": "Falta de IPS en el barrio", "slug": "falta-ips", "icono": "x-circle", "orden": 1},
    {"subsector_slug": "acceso-salud", "nombre": "Largas listas de espera", "slug": "listas-espera", "icono": "x-circle", "orden": 2},
    {"subsector_slug": "acceso-salud", "nombre": "Falta de medicamentos", "slug": "falta-medicamentos", "icono": "x-circle", "orden": 3},
    # Salud → Salud mental
    {"subsector_slug": "salud-mental", "nombre": "Falta de atención psicológica", "slug": "falta-atencion-psicologica", "icono": "x-circle", "orden": 1},
    {"subsector_slug": "salud-mental", "nombre": "Estres laboral", "slug": "estres-laboral", "icono": "x-circle", "orden": 2},
    # Salud → Nutrición
    {"subsector_slug": "nutricion", "nombre": "Inseguridad alimentaria", "slug": "inseguridad-alimentaria", "icono": "x-circle", "orden": 1},
    {"subsector_slug": "nutricion", "nombre": "Desnutrición infantil", "slug": "desnutricion-infantil", "icono": "x-circle", "orden": 2},
    # Educación → Calidad educativa
    {"subsector_slug": "calidad-educativa", "nombre": "Baja calidad de enseñanza", "slug": "baja-calidad-ensenanza", "icono": "x-circle", "orden": 1},
    {"subsector_slug": "calidad-educativa", "nombre": "Falta de docentes", "slug": "falta-docentes", "icono": "x-circle", "orden": 2},
    {"subsector_slug": "calidad-educativa", "nombre": "Deserción escolar", "slug": "desercion-escolar", "icono": "x-circle", "orden": 3},
    # Educación → Infraestructura educativa
    {"subsector_slug": "infraestructura-educativa", "nombre": "Colegios deteriorados", "slug": "colegios-deteriorados", "icono": "x-circle", "orden": 1},
    {"subsector_slug": "infraestructura-educativa", "nombre": "Falta de tecnología", "slug": "falta-tecnologia", "icono": "x-circle", "orden": 2},
    # Educación → Acceso cultural
    {"subsector_slug": "acceso-cultural", "nombre": "Falta de bibliotecas", "slug": "falta-bibliotecas", "icono": "x-circle", "orden": 1},
    {"subsector_slug": "acceso-cultural", "nombre": "Poca oferta cultural", "slug": "poca-oferta-cultural", "icono": "x-circle", "orden": 2},
    # Gobierno → Transparencia
    {"subsector_slug": "transparencia", "nombre": "Obras públicas sin ejecutar", "slug": "obras-sin-ejecutar", "icono": "x-circle", "orden": 1},
    {"subsector_slug": "transparencia", "nombre": "Mal uso de recursos", "slug": "mal-uso-recursos", "icono": "x-circle", "orden": 2},
    # Gobierno → Participación ciudadana
    {"subsector_slug": "participacion-ciudadana", "nombre": "Desconexión con autoridades", "slug": "desconexion-autoridades", "icono": "x-circle", "orden": 1},
    {"subsector_slug": "participacion-ciudadana", "nombre": "Falta de rendición de cuentas", "slug": "falta-rendicion-cuentas", "icono": "x-circle", "orden": 2},
    # Gobierno → Contratación pública
    {"subsector_slug": "contratacion-publica", "nombre": "Corrupción en contratación", "slug": "corrupcion-contratacion", "icono": "x-circle", "orden": 1},
    {"subsector_slug": "contratacion-publica", "nombre": "Clientelismo", "slug": "clientelismo", "icono": "x-circle", "orden": 2},
    # Campo → Agricultura
    {"subsector_slug": "agricultura", "nombre": "Falta de tierra", "slug": "falta-tierra", "icono": "x-circle", "orden": 1},
    {"subsector_slug": "agricultura", "nombre": "Bajos precios del campo", "slug": "bajos-precios-campo", "icono": "x-circle", "orden": 2},
    {"subsector_slug": "agricultura", "nombre": "Falta de asistencia técnica", "slug": "falta-asistencia-tecnica", "icono": "x-circle", "orden": 3},
    # Campo → Reforma rural
    {"subsector_slug": "reforma-rural", "nombre": "Violencia rural", "slug": "violencia-rural", "icono": "x-circle", "orden": 1},
    {"subsector_slug": "reforma-rural", "nombre": "Desplazamiento forzado", "slug": "desplazamiento-forzado", "icono": "x-circle", "orden": 2},
    # Campo → Protección ambiental
    {"subsector_slug": "proteccion-ambiental", "nombre": "Deforestación", "slug": "deforestacion", "icono": "x-circle", "orden": 1},
    {"subsector_slug": "proteccion-ambiental", "nombre": "Contaminación del aire", "slug": "contaminacion-aire", "icono": "x-circle", "orden": 2},
    {"subsector_slug": "proteccion-ambiental", "nombre": "Contaminación de ríos", "slug": "contaminacion-rios", "icono": "x-circle", "orden": 3},
    # Campo → Recursos hídricos
    {"subsector_slug": "recursos-hidricos", "nombre": "Falta de agua potable", "slug": "falta-agua-potable", "icono": "x-circle", "orden": 1},
    {"subsector_slug": "recursos-hidricos", "nombre": "Sequías prolongadas", "slug": "sequias-prolongadas", "icono": "x-circle", "orden": 2},
    # Infraestructura → Vías y transporte
    {"subsector_slug": "vias-transporte", "nombre": "Mal estado de vías", "slug": "mal-estado-vias", "icono": "x-circle", "orden": 1},
    {"subsector_slug": "vias-transporte", "nombre": "Falta de transporte público", "slug": "falta-transporte-publico", "icono": "x-circle", "orden": 2},
    # Infraestructura → Agua y saneamiento
    {"subsector_slug": "agua-saneamiento", "nombre": "Falta de acueducto", "slug": "falta-acueducto", "icono": "x-circle", "orden": 1},
    {"subsector_slug": "agua-saneamiento", "nombre": "Falta de alcantarillado", "slug": "falta-alcantarillado", "icono": "x-circle", "orden": 2},
    # Infraestructura → Vivienda
    {"subsector_slug": "vivienda", "nombre": "Déficit de vivienda", "slug": "deficit-vivienda", "icono": "x-circle", "orden": 1},
    {"subsector_slug": "vivienda", "nombre": "Viviendas en mal estado", "slug": "viviendas-mal-estado", "icono": "x-circle", "orden": 2},
    # Infraestructura → Conectividad
    {"subsector_slug": "conectividad", "nombre": "Falta de internet", "slug": "falta-internet", "icono": "x-circle", "orden": 1},
    {"subsector_slug": "conectividad", "nombre": "Zonas sin cobertura", "slug": "zonas-sin-cobertura", "icono": "x-circle", "orden": 2},
    # Género, Juventud y Comunidad → Equidad de género
    {"subsector_slug": "equidad-genero", "nombre": "Brecha salarial de género", "slug": "brecha-salarial-genero", "icono": "x-circle", "orden": 1},
    {"subsector_slug": "equidad-genero", "nombre": "Falta de equidad laboral", "slug": "falta-equidad-laboral", "icono": "x-circle", "orden": 2},
    # Género, Juventud y Comunidad → Oportunidades juveniles
    {"subsector_slug": "oportunidades-juveniles", "nombre": "Falta de oportunidades", "slug": "falta-oportunidades-juveniles", "icono": "x-circle", "orden": 1},
    {"subsector_slug": "oportunidades-juveniles", "nombre": "Drogadicción juvenil", "slug": "drogadiccion-juvenil", "icono": "x-circle", "orden": 2},
    # Género, Juventud y Comunidad → Adultos mayores
    {"subsector_slug": "adultos-mayores", "nombre": "Abandono de adultos mayores", "slug": "abandono-adultos-mayores", "icono": "x-circle", "orden": 1},
    {"subsector_slug": "adultos-mayores", "nombre": "Falta de pensiones", "slug": "falta-pensiones", "icono": "x-circle", "orden": 2},
]

# ---------------------------------------------------------------------
# 6. Mapping problema_slug → pilar_orden (para SRIE)
# ---------------------------------------------------------------------
PROBLEMA_PILAR_MAP: dict[str, int | None] = {
    # Empleo → Minero-Energético (orden 10)
    "falta-empleo-formal": 10, "desempleo-juvenil": 10, "falta-capital-semilla": 10,
    "tramites-formalizar": 10, "impuestos-altos": 10, "informalidad-laboral": 10,
    # Seguridad → Seguridad (orden 5)
    "inseguridad-barrios": 5, "robo-hurto": 5, "extorsion": 5,
    "violencia-mujer": 9, "maltrato-infantil": 9,
    "narcotrafico": 5, "microtrafico": 5,
    # Salud → Salud (orden 7)
    "falta-ips": 7, "listas-espera": 7, "falta-medicamentos": 7,
    "falta-atencion-psicologica": 7, "estres-laboral": 7,
    "inseguridad-alimentaria": 7, "desnutricion-infantil": 7,
    # Educación → Educación (orden 11)
    "baja-calidad-ensenanza": 11, "falta-docentes": 11, "desercion-escolar": 11,
    "colegios-deteriorados": 11, "falta-tecnologia": 11,
    "falta-bibliotecas": 12, "poca-oferta-cultural": 12,
    # Gobierno → Corrupción (orden 6)
    "obras-sin-ejecutar": 6, "mal-uso-recursos": 6,
    "desconexion-autoridades": 6, "falta-rendicion-cuentas": 6,
    "corrupcion-contratacion": 6, "clientelismo": 6,
    # Campo → Campo y Agro (orden 8) / Medioambiente (orden 13)
    "falta-tierra": 8, "bajos-precios-campo": 8, "falta-asistencia-tecnica": 8,
    "violencia-rural": 5, "desplazamiento-forzado": 5,
    "deforestacion": 13, "contaminacion-aire": 13, "contaminacion-rios": 13,
    "falta-agua-potable": 8, "sequias-prolongadas": 8,
    # Infraestructura
    "mal-estado-vias": 10, "falta-transporte-publico": 10,
    "falta-acueducto": 10, "falta-alcantarillado": 10,
    "deficit-vivienda": 10, "viviendas-mal-estado": 10,
    "falta-internet": 10, "zonas-sin-cobertura": 10,
    # Género, Juventud
    "brecha-salarial-genero": 9, "falta-equidad-laboral": 9,
    "falta-oportunidades-juveniles": 17, "drogadiccion-juvenil": 17,
    "abandono-adultos-mayores": 17, "falta-pensiones": 17,
}

# ---------------------------------------------------------------------
# 7. Actores (10)
# ---------------------------------------------------------------------
ACTORES: list[dict] = [
    {"nombre": "Gobierno Nacional", "slug": "gobierno-nacional", "icono": "flag", "orden": 1},
    {"nombre": "Gobernación", "slug": "gobernacion", "icono": "building", "orden": 2},
    {"nombre": "Alcaldía", "slug": "alcaldia", "icono": "house-gear", "orden": 3},
    {"nombre": "Empresa Privada", "slug": "empresa-privada", "icono": "briefcase", "orden": 4},
    {"nombre": "Academia", "slug": "academia", "icono": "mortarboard", "orden": 5},
    {"nombre": "Comunidad Organizada", "slug": "comunidad-organizada", "icono": "people", "orden": 6},
    {"nombre": "ONG y Sociedad Civil", "slug": "ong-sociedad-civil", "icono": "heart", "orden": 7},
    {"nombre": "Iglesias y Organizaciones Religiosas", "slug": "iglesias", "icono": "house-door", "orden": 8},
    {"nombre": "Fuerzas Militares y Policía", "slug": "fuerzas-militares", "icono": "shield", "orden": 9},
    {"nombre": "Medios de Comunicación", "slug": "medios-comunicacion", "icono": "newspaper", "orden": 10},
]

# ---------------------------------------------------------------------
# 8. Beneficiarios (10)
# ---------------------------------------------------------------------
BENEFICIARIOS: list[dict] = [
    {"nombre": "Niños y niñas", "slug": "ninos", "icono": "emoji-smile", "orden": 1},
    {"nombre": "Jóvenes", "slug": "jovenes", "icono": "emoji-laughing", "orden": 2},
    {"nombre": "Mujeres", "slug": "mujeres", "icono": "gender-female", "orden": 3},
    {"nombre": "Adultos mayores", "slug": "adultos-mayores", "icono": "person-standing", "orden": 4},
    {"nombre": "Campesinos y agricultores", "slug": "campesinos", "icono": "crop", "orden": 5},
    {"nombre": "Pueblos indígenas", "slug": "indigenas", "icono": "globe", "orden": 6},
    {"nombre": "Comunidades afrocolombianas", "slug": "afrocolombianos", "icono": "people", "orden": 7},
    {"nombre": "Personas con discapacidad", "slug": "discapacidad", "icono": "universal-access", "orden": 8},
    {"nombre": "Empresarios y comerciantes", "slug": "empresarios", "icono": "shop", "orden": 9},
    {"nombre": "Toda la comunidad", "slug": "todos", "icono": "globe2", "orden": 10},
]


def _slugify(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    texto = re.sub(r"[^\w\s-]", "", texto).strip().lower()
    return re.sub(r"[\s_-]+", "-", texto)


def seed_plan() -> None:
    """Siembra el plan estratégico con sus 18 pilares."""
    if Plan.query.filter_by(nombre=PLAN_NOMBRE).first():
        print("  Plan ya existe, no se vuelve a sembrar.")
        return

    plan = Plan(
        nombre=PLAN_NOMBRE, version="1.0", ambito="nacional",
        vigencia_inicio=date(2026, 8, 7), vigencia_fin=date(2030, 8, 6),
        activo=True,
    )
    db.session.add(plan)
    db.session.flush()

    pilar_democratico = None
    for p in PILARES:
        pilar = Pilar(
            plan_id=plan.id, nombre=p["nombre"],
            slug=p.get("slug") or _slugify(p["nombre"]),
            tipo=p["tipo"], orden=p["orden"],
        )
        db.session.add(pilar)
        db.session.flush()
        if p["nombre"].startswith("Pilar Democrático"):
            pilar_democratico = pilar
            for i, nombre_linea in enumerate(LINEAS_PILAR_DEMOCRATICO):
                db.session.add(LineaEstrategica(pilar_id=pilar.id, nombre=nombre_linea, orden=i))
        else:
            db.session.add(LineaEstrategica(
                pilar_id=pilar.id, nombre=f"Línea general — {p['nombre']}", orden=0,
                descripcion="Pendiente de desglose en líneas/componentes/objetivos específicos.",
            ))

    if pilar_democratico:
        primera_linea = LineaEstrategica.query.filter_by(pilar_id=pilar_democratico.id, orden=0).first()
        if primera_linea:
            componente = Componente(linea_id=primera_linea.id, nombre="Reconocimiento constitucional del vínculo cívico")
            db.session.add(componente)
            db.session.flush()
            db.session.add(Objetivo(
                componente_id=componente.id,
                nombre="Fortalecer la adhesión ciudadana a la Constitución de 1991", ods="16",
            ))

    db.session.commit()
    print(f"  Plan '{plan.nombre}' sembrado con {len(PILARES)} pilares.")


def seed_sectores() -> None:
    """Siembra sectores, subsectores y problemas del catálogo."""
    if Sector.query.count() > 0:
        print("  Sectores ya existen, no se vuelve a sembrar.")
        return

    # Sectores
    sector_map: dict[str, Sector] = {}
    for s in SECTORES:
        sector = Sector(**s, activo=True)
        db.session.add(sector)
        db.session.flush()
        sector_map[s["slug"]] = sector

    # Subsectores
    subsector_map: dict[str, Subsector] = {}
    for s in SUBSECTORES:
        sector = sector_map[s.pop("sector_slug")]
        sub = Subsector(sector_id=sector.id, **s, activo=True)
        db.session.add(sub)
        db.session.flush()
        subsector_map[s["slug"]] = sub

    # Problemas
    for p in PROBLEMAS_CATALOGO:
        sub = subsector_map[p.pop("subsector_slug")]
        db.session.add(ProblemaCatalogo(subsector_id=sub.id, **p, activo=True))

    db.session.commit()
    print(f"  {len(SECTORES)} sectores, {len(SUBSECTORES)} subsectores, {len(PROBLEMAS_CATALOGO)} problemas sembrados.")


def seed_actores_beneficiarios() -> None:
    """Siembra catálogos de actores y beneficiarios."""
    if Actor.query.count() > 0:
        print("  Actores y beneficiarios ya existen, no se vuelve a sembrar.")
        return

    for a in ACTORES:
        db.session.add(Actor(**a, activo=True))
    for b in BENEFICIARIOS:
        db.session.add(Beneficiario(**b, activo=True))

    db.session.commit()
    print(f"  {len(ACTORES)} actores, {len(BENEFICIARIOS)} beneficiarios sembrados.")


def run_all() -> None:
    """Ejecuta todos los seeds en orden."""
    print("=== Sembrando datos V3 (evolución) ===")
    seed_plan()
    seed_sectores()
    seed_actores_beneficiarios()
    print("=== Seed completado ===")
