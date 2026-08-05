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
from app.models.politica import Politica
from app.models.miembro import MiembroEquipo


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


# ---------------------------------------------------------------------
# 9. Políticas públicas (Catálogo V2 portado)
# ---------------------------------------------------------------------
POLITICAS: list[dict] = [
    {
        "titulo": "Familias en Acción",
        "sector_nombre": "Empleo y Economía",
        "resumen_ejecutivo": "Programa de transferencias monetarias condicionadas del Gobierno Nacional que entrega subsidios a familias en situación de pobreza y vulnerabilidad, a cambio del cumplimiento de corresponsabilidades en salud y educación de sus hijos.",
        "problema": "Colombia enfrenta altos niveles de pobreza monetaria y multidimensional, especialmente en zonas rurales y urbanas marginadas. Muchas familias no tienen ingresos suficientes para cubrir necesidades básicas y los niños abandonan la escuela por falta de recursos.",
        "objetivos": "Reducir la pobreza y la desigualdad en hogares vulnerables; Fomentar la inversión en capital humano mediante corresponsabilidades en salud y educación; Romper la transmisión intergeneracional de la pobreza",
        "poblacion_objetivo": "Familias en situación de pobreza y vulnerabilidad con niños, niñas y adolescentes menores de 18 años",
        "normatividad": "CONPES Social; Ley 1532 de 2012; Decreto Reglamentario",
        "cronologia": "2001: Creación del programa Familias en Acción; 2007: Se integra a la Red Juntos; 2012: Se expide la Ley 1532 que lo formaliza; 2022: Se fusiona con Ingreso Solidario; 2026: Más de 4 millones de familias beneficiadas",
        "entidades_responsables": "Departamento para la Prosperidad Social (DPS); Ministerio de Salud y Protección Social; Ministerio de Educación Nacional",
        "indicadores": "Cobertura: 4 millones de familias; Tasa de escolaridad: 15% de aumento en zonas rurales; Controles de salud: 90% de cumplimiento",
        "presupuesto": "$3.5 billones anuales",
        "estado": "Activa",
        "ods_relacionados": "1, 2, 3, 4, 10",
        "alcance": "Nacional",
        "documentos": "Ley 1532 de 2012; CONPES 3798; Informe de resultados DPS 2025",
    },
    {
        "titulo": "Política Nacional de Cambio Climático",
        "sector_nombre": "Campo, Agro y Medio Ambiente",
        "resumen_ejecutivo": "Estrategia nacional que busca reducir las emisiones de gases de efecto invernadero y adaptar al país a los efectos del cambio climático, con metas concretas a 2030 y 2050, integrando la variable climática en la planeación territorial y sectorial.",
        "problema": "Colombia es uno de los países más vulnerables al cambio climático debido a su ubicación geográfica y características socioeconómicas. Fenómenos como inundaciones, sequías y deslizamientos afectan cada año a miles de colombianos y generan pérdidas económicas significativas.",
        "objetivos": "Reducir las emisiones de GEI en un 51% para 2030; Alcanzar la carbono neutralidad a 2050; Integrar el cambio climático en la planeación de 32 departamentos; Fortalecer la capacidad de adaptación de comunidades vulnerables",
        "poblacion_objetivo": "Toda la población colombiana, con énfasis en comunidades vulnerables al cambio climático",
        "normatividad": "Ley 1931 de 2018 (Ley de Cambio Climático); CONPES 3700; CONPES 4023; NDC Actualizada 2020",
        "cronologia": "2015: Colombia firma el Acuerdo de París; 2018: Se expide la Ley 1931 de Cambio Climático; 2020: Se actualiza la NDC con metas más ambiciosas; 2022: Se adopta la Estrategia Climática de Largo Plazo (E2050); 2025: Reporte de avance: 30% de reducción de emisiones",
        "entidades_responsables": "Ministerio de Ambiente y Desarrollo Sostenible; IDEAM; Corporaciones Autónomas Regionales; Gobernaciones y Alcaldías",
        "indicadores": "Reducción de emisiones: 30% a 2025; Departamentos con planes de cambio climático: 32/32; Inversión en adaptación: $2 billones",
        "presupuesto": "$4 billones (públicos y privados)",
        "estado": "Activa",
        "ods_relacionados": "7, 11, 12, 13, 14, 15",
        "alcance": "Nacional",
        "documentos": "Ley 1931 de 2018; CONPES 4023; NDC Colombia 2020; E2050",
    },
    {
        "titulo": "Jornada Única Escolar",
        "sector_nombre": "Educación y Cultura",
        "resumen_ejecutivo": "Política educativa que amplía el tiempo de permanencia de los estudiantes en instituciones educativas oficiales, pasando de media jornada (4 horas) a jornada completa (7 horas), para mejorar la calidad educativa y reducir la exposición a riesgos sociales.",
        "problema": "La mayoría de instituciones educativas públicas en Colombia operaban con jornadas de media jornada (4 horas), lo que limitaba el tiempo de aprendizaje y exponía a los estudiantes a riesgos sociales en las horas no escolarizadas.",
        "objetivos": "Ampliar la jornada escolar a 7 horas diarias en instituciones oficiales; Mejorar la calidad educativa mediante más tiempo de aprendizaje; Reducir la exposición de niños y jóvenes a riesgos sociales; Fortalecer actividades extracurriculares (deporte, cultura, tecnología)",
        "poblacion_objetivo": "Estudiantes de instituciones educativas oficiales en todo el territorio nacional",
        "normatividad": "Ley 1753 de 2015 (PND); Decreto 501 de 2016; Directiva Ministerial 05 de 2016",
        "cronologia": "2015: Se incluye en el Plan Nacional de Desarrollo; 2016: Se expide el Decreto que reglamenta la Jornada Única; 2018: 1.000 sedes educativas implementan la jornada única; 2022: Se amplía la cobertura a zonas rurales; 2025: Más de 50.000 estudiantes beneficiados",
        "entidades_responsables": "Ministerio de Educación Nacional; Secretarías de Educación Departamentales y Municipales; Entidades Territoriales Certificadas",
        "indicadores": "Estudiantes beneficiados: 50.000+; Sedes educativas: 1.000+; Horas de jornada: 7 horas diarias",
        "presupuesto": "$800.000 millones anuales",
        "estado": "En formulación",
        "ods_relacionados": "4, 10",
        "alcance": "Nacional",
        "documentos": "Ley 1753 de 2015; Decreto 501 de 2016; Informe MEN de implementación",
    },
    {
        "titulo": "Mi Casa Ya",
        "sector_nombre": "Infraestructura y Servicios",
        "resumen_ejecutivo": "Programa de subsidios del Gobierno Nacional que facilita la compra de vivienda nueva a hogares de ingresos bajos y medios, mediante un subsidio a la cuota inicial y una cobertura a la tasa de interés del crédito hipotecario.",
        "problema": "Déficit habitacional cuantitativo y cualitativo que afecta a millones de colombianos. Los hogares de bajos ingresos no pueden acceder a vivienda formal por falta de ahorro para la cuota inicial y altas tasas de interés hipotecario.",
        "objetivos": "Facilitar el acceso a vivienda nueva a hogares de ingresos bajos y medios; Reducir el déficit habitacional; Dinamizar el sector de la construcción; Generar empleo en el sector",
        "poblacion_objetivo": "Hogares con ingresos hasta 4 SMMLV que no sean propietarios de vivienda",
        "normatividad": "Ley 1537 de 2012; Decreto 1259 de 2023; Resolución MVCT",
        "cronologia": "2015: Se crea el programa Mi Casa Ya; 2018: Se amplía el subsidio a hogares de ingresos medios; 2022: Se incrementa el valor del subsidio; 2024: Más de 300.000 hogares beneficiados; 2026: Nuevas condiciones y montos actualizados",
        "entidades_responsables": "Ministerio de Vivienda, Ciudad y Territorio; Fondo Nacional de Vivienda (Fonvivienda); Entidades financieras",
        "indicadores": "Hogares beneficiados: 300.000+; Subsidio máximo: $30 millones; Cobertura de tasa: hasta 5 puntos porcentuales",
        "presupuesto": "$1.5 billones anuales",
        "estado": "Activa",
        "ods_relacionados": "1, 8, 11",
        "alcance": "Nacional",
        "documentos": "Ley 1537 de 2012; Decreto 1259 de 2023; Reglamento operativo Fonvivienda",
    },
    {
        "titulo": "Política Nacional de Salud Mental",
        "sector_nombre": "Salud y Bienestar",
        "resumen_ejecutivo": "Estrategia integral del Gobierno Nacional para promover la salud mental, prevenir los trastornos mentales y garantizar la atención oportuna y de calidad a las personas que enfrentan problemas de salud mental en Colombia.",
        "problema": "La salud mental en Colombia ha sido históricamente subpriorizada. La prevalencia de trastornos mentales es alta (depresión, ansiedad, suicidio) y los servicios de atención son insuficientes, especialmente en zonas rurales. La pandemia agravó esta situación.",
        "objetivos": "Reducir la prevalencia de trastornos mentales en la población colombiana; Fortalecer la red de servicios de salud mental; Prevenir el suicidio y las conductas autolesivas; Promover el bienestar emocional desde la infancia; Integrar la salud mental en todos los niveles de atención",
        "poblacion_objetivo": "Toda la población colombiana, con énfasis en niños, adolescentes, adultos mayores y víctimas del conflicto",
        "normatividad": "Ley 1616 de 2013 (Ley de Salud Mental); CONPES 3992; Resolución 518 de 2015",
        "cronologia": "2013: Se expide la Ley 1616 de Salud Mental; 2015: Se adopta la Política Nacional de Salud Mental; 2018: Se crea el programa de prevención del suicidio; 2022: Se fortalecen los servicios comunitarios de salud mental; 2025: Se amplía la cobertura a 1.000 municipios",
        "entidades_responsables": "Ministerio de Salud y Protección Social; EPS e IPS; Secretarías de Salud Departamentales y Municipales; ICBF",
        "indicadores": "Cobertura de servicios: 1.000 municipios; Línea de atención: 24/7; Psicólogos por cada 10.000 hab: 15",
        "presupuesto": "$1.2 billones anuales",
        "estado": "Activa",
        "ods_relacionados": "3, 10, 16",
        "alcance": "Nacional",
        "documentos": "Ley 1616 de 2013; CONPES 3992; Lineamientos técnicos MSPS",
    },
    {
        "titulo": "Estrategia de Gobierno Digital",
        "sector_nombre": "Gobierno y Corrupción",
        "resumen_ejecutivo": "Política del Gobierno Nacional para transformar la administración pública mediante la digitalización de trámites, la interoperabilidad de sistemas y la prestación de servicios digitales centrados en el ciudadano.",
        "problema": "Los ciudadanos enfrentan largas filas, trámites presenciales, duplicidad de información y baja eficiencia en la gestión pública. La brecha digital limita el acceso a servicios del Estado.",
        "objetivos": "Digitalizar el 100% de los trámites de alta demanda; Implementar interoperabilidad entre entidades del Estado; Reducir tiempos y costos de trámites para los ciudadanos; Garantizar acceso inclusivo a servicios digitales",
        "poblacion_objetivo": "Todos los ciudadanos colombianos que realizan trámites ante el Estado",
        "normatividad": "Ley 1955 de 2019 (PND); Decreto 620 de 2020; CONPES 3975; Ley de TIC",
        "cronologia": "2018: Se formula la Política de Gobierno Digital; 2020: Se expide el Decreto 620 de Transformación Digital; 2021: Se lanza la plataforma GOV.CO; 2023: Más de 5.000 trámites digitalizados; 2025: Interoperabilidad entre 200 entidades",
        "entidades_responsables": "Ministerio de Tecnologías de la Información y Comunicaciones (Mintic); Departamento Administrativo de la Función Pública; Entidades del orden nacional y territorial",
        "indicadores": "Trámites digitalizados: 5.000+; Entidades interoperables: 200+; Usuarios de GOV.CO: 10 millones",
        "presupuesto": "$500.000 millones anuales",
        "estado": "Activa",
        "ods_relacionados": "9, 16, 17",
        "alcance": "Nacional",
        "documentos": "Decreto 620 de 2020; CONPES 3975; Manual de Gobierno Digital",
    },
]

MIEMBROS: list[dict] = [
    {
        "nombre": "David David B.",
        "cargo": "Fundador y Director",
        "descripcion": "Creador del Laboratorio de Inteligencia Pública y del motor SRIE. Ingeniero y científico de datos con experiencia en inteligencia estratégica, análisis de políticas públicas y sistemas participativos.",
        "orden": 1,
    },
    {
        "nombre": "Stonelytics",
        "cargo": "Laboratorio de Innovación",
        "descripcion": "Equipo multidisciplinario de tecnología, ciencia de datos, diseño y políticas públicas comprometido con la transformación digital del Estado colombiano.",
        "orden": 2,
    },
    {
        "nombre": "Comunidad SRIE",
        "cargo": "Red de Colaboradores",
        "descripcion": "Ciudadanos, académicos y funcionarios públicos que contribuyen a la evolución del Sistema de Reconocimiento e Inteligencia Estratégica.",
        "orden": 3,
    },
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


def seed_politicas() -> None:
    """Siembra políticas públicas desde el catálogo V2 portado."""
    if Politica.query.count() > 0:
        print("  Políticas ya existen, no se vuelve a sembrar.")
        return

    for p in POLITICAS:
        sector_nombre = p.pop("sector_nombre")
        sector = Sector.query.filter_by(nombre=sector_nombre).first()
        politica = Politica(**p, sector_id=sector.id if sector else None, activo=True)
        db.session.add(politica)

    db.session.commit()
    print(f"  {len(POLITICAS)} políticas públicas sembradas.")


def seed_miembros() -> None:
    """Siembra miembros del equipo."""
    if MiembroEquipo.query.count() > 0:
        print("  Miembros ya existen, no se vuelve a sembrar.")
        return

    for m in MIEMBROS:
        db.session.add(MiembroEquipo(**m, activo=True))

    db.session.commit()
    print(f"  {len(MIEMBROS)} miembros del equipo sembrados.")


def run_all() -> None:
    """Ejecuta todos los seeds en orden."""
    print("=== Sembrando datos V3 (evolución) ===")
    seed_plan()
    seed_sectores()
    seed_actores_beneficiarios()
    seed_politicas()
    seed_miembros()
    print("=== Seed completado ===")
