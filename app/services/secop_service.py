"""Ingesta y consulta de procesos SECOP II (contratación pública de Colombia).

Port del pipeline de Radar_SECOP (`scripts/update-data.mjs`) a Python:
descarga paginada de datos.gov.co → filtros (oferta abierta, fecha >= corte) →
normalización → validación estricta (si la data no pasa, no se publica) →
persistencia en PostgreSQL (`SecopProceso` / `SecopCorte`).

Fuente: dataset SECOP II de datos.gov.co (`p6dx-8zbt`).
"""
from __future__ import annotations

import json
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timezone

from app import db
from app.models.secop import SecopCorte, SecopProceso
from app.services.hora_local import hoy_bogota

API_BASE = "https://www.datos.gov.co/resource/p6dx-8zbt.json"
PAGE_SIZE = 5000
MAX_PAGES = 50  # cap de seguridad

# Modalidades que NO exigen RUP inscrito.
SIN_RUP = {"Mínima cuantía"}

# Temas por coincidencia de palabras clave sobre entidad + nombre del proceso.
TEMAS = {
    "Tecnología / IA / Datos": [
        "inteligencia artificial", "automatizacion", "automatización", "robot",
        "machine learning", "software", "plataforma tecnologic", "sistema tecnologic",
        "digitalizacion", "digitalización", "datos", "ciberseguridad", "transformacion digital",
        "biometr", "tics", "sistematizacion", "conectividad", "internet de las cosas",
    ],
    "Desarrollo económico / Emprendimiento": [
        "emprendimiento", "desarrollo economico", "desarrollo económico", "unidad productiva",
        "mipyme", "microempres", "agroindustria", "comercializacion", "asociatividad",
        "productividad", "feria empresarial", "turismo", "cluster",
    ],
    "Capacitación / Gestión documental": [
        "capacitacion", "capacitación", "formacion", "formación", "entrenamiento",
        "gestion documental", "gestión documental", "archivo", "sg-sst", "sgh",
        "talento humano", "fortalecimiento institucional", "seminario",
    ],
    "Infraestructura / Obra pública": [
        "construccion", "construcción", "obra publica", "obra pública", "vias", "vías",
        "pavimentacion", "puente", "acueducto", "alcantarillado", "planta de tratamiento",
        "infraestructura", "mantenimiento vial", "edificacion", "adecuacion", "mejoramiento de vivienda",
    ],
    "Salud / Educación / Social": [
        "salud", "hospital", "equipo biomedico", "medicamentos", "vacunacion", "educacion",
        "colegio", "dotacion escolar", "uniformes", "alimentacion escolar", "atencion psicosocial",
        "poblacion vulnerable", "inclusion", "discapacidad",
    ],
    "Seguridad / Convivencia": [
        "seguridad", "vigilancia", "cctv", "camaras", "convivencia", "prevencion del delito",
        "policia", "seguridad ciudadana", "emergencias",
    ],
    "Ambiente / Sostenibilidad": [
        "ambiental", "medio ambiente", "reforestacion", "parques", "reciclaje", "residuos",
        "energias renovables", "solar", "eficiencia energetica", "cambio climatico", "agua potable",
    ],
}

# Cross-ref con pilares SRIE de LIP (slugs del motor SRIE).
PILAR_KEYWORDS: dict[str, list[str]] = {
    "iluminar-la-patria": ["energia", "electricidad", "solar", "renovable", "tecnologia", "internet", "digital", "fibra", "banda ancha", "subestacion", "iluminacion", "alumbrado"],
    "recuperar-la-salud": ["salud", "hospital", "clinica", "ips", "medico", "medicamentos", "vacuna", "ambulancia", "urgencias", "biomedico"],
    "educacion": ["educacion", "colegio", "universidad", "docente", "estudiante", "escolar", "biblioteca", "sena", "dotacion escolar", "uniformes"],
    "seguridad": ["seguridad", "vigilancia", "cctv", "camara", "policia", "convivencia", "emergencias", "prevencion del delito"],
    "erradicar-la-corrupcion": ["transparencia", "rendicion", "contratacion", "control interno", "auditoria", "contraloria", "procuraduria"],
    "campo-y-el-agro": ["agro", "agricultura", "campesino", "ganaderia", "cafe", "arroz", "riego", "maquinaria agricola", "finca", "cosecha"],
    "proteger-el-medioambiente": ["ambiental", "medio ambiente", "bosque", "reciclaje", "residuos", "reforestacion", "paramo", "agua potable", "saneamiento"],
    "minero-energetico": ["mineria", "petroleo", "gas", "carbon", "energia", "infraestructura", "vial", "transporte", "vias", "puente", "acueducto", "alcantarillado", "vivienda", "aeropuerto", "puerto"],
    "cultura": ["cultura", "musica", "teatro", "patrimonio", "turismo", "deporte", "recreacion", "eventos"],
    "patria-para-las-mujeres": ["mujer", "mujeres", "genero", "violencia de genero", "equidad"],
    "los-jovenes": ["joven", "jovenes", "adolescente", "emprendedor", "oportunidad", "deporte"],
    "pilar-democratico": ["constitucion", "democracia", "participacion ciudadana", "rendicion", "debido proceso", "garantias"],
}

URL_OK = re.compile(r"^https?://.+\bnoticeUID=", re.IGNORECASE)
FECHA_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class SecopError(Exception):
    """Error de la ingesta SECOP (no se publican datos corruptos)."""


def normalize(texto) -> str:
    return re.sub(r"\s+", " ", str(texto or "").replace("\u00A0", " ")).strip()


def dias_entre(desde: date, hasta: date) -> int:
    return (hasta - desde).days


def detectar_temas(texto: str) -> list[str]:
    t = normalize(texto).lower()
    return [nombre for nombre, kws in TEMAS.items() if any(kw in t for kw in kws)]


def detectar_pilares(texto: str) -> list[str]:
    t = normalize(texto).lower()
    return [slug for slug, kws in PILAR_KEYWORDS.items() if any(kw in t for kw in kws)]


def validar(records: list[dict]) -> list[str]:
    """Valida registros normalizados; retorna lista de errores (vacía = OK)."""
    REQUIRED = ["e", "d", "c", "n", "m", "t"]
    errors: list[str] = []
    for i, r in enumerate(records):
        for k in REQUIRED:
            if not r.get(k):
                errors.append(f"[{i}] campo '{k}' vacío")
        if not isinstance(r.get("v"), (int, float)) or r["v"] < 0:
            errors.append(f"[{i}] v inválido: {r.get('v')}")
        if not isinstance(r.get("rup"), bool):
            errors.append(f"[{i}] rup no es boolean")
        if not isinstance(r.get("dl"), (int, float)) or r["dl"] < 0:
            errors.append(f"[{i}] dl inválido: {r.get('dl')}")
        if not FECHA_RE.match(r.get("f") or ""):
            errors.append(f"[{i}] f inválida: {r.get('f')}")
        if not r.get("u") or not URL_OK.match(r.get("u") or ""):
            errors.append(f"[{i}] u inválida: {r.get('u')}")
        if not isinstance(r.get("tm"), list):
            errors.append(f"[{i}] tm no es array")
    return errors


def _fetch_paginated(params: dict[str, str]) -> list[dict]:
    rows: list[dict] = []
    offset = 0
    for _ in range(MAX_PAGES):
        query = dict(params)
        query["$limit"] = str(PAGE_SIZE)
        query["$offset"] = str(offset)
        url = f"{API_BASE}?{urllib.parse.urlencode(query)}"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "LIP-SECOP/1.0 (+https://inteligenciapublica.stonelytics.tech)"},
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            batch = json.loads(resp.read().decode("utf-8"))
        rows.extend(batch)
        if len(batch) < PAGE_SIZE:
            break
        offset += PAGE_SIZE
    return rows


def _normalizar_registros(raw_rows: list[dict], corte: date) -> list[dict]:
    """Normaliza filas brutas de la API al esquema compacto del visor."""
    out: list[dict] = []
    for r in raw_rows:
        f = (r.get("fecha_de_recepcion_de") or "")[:10]
        if not FECHA_RE.match(f) or f < corte.isoformat():
            continue
        nombre = normalize(r.get("nombre_del_procedimiento"))
        modalidad = normalize(r.get("modalidad_de_contratacion"))
        try:
            valor = round(float(str(r.get("precio_base") or "0").replace(",", ".")))
        except ValueError:
            valor = 0
        u = (r.get("urlproceso") or {}).get("url", "") if isinstance(r.get("urlproceso"), dict) else ""
        if not URL_OK.match(u):
            continue
        texto = f"{r.get('entidad') or ''} {nombre}"
        out.append({
            "e": normalize(r.get("entidad")),
            "d": normalize(r.get("departamento_entidad")),
            "c": normalize(r.get("ciudad_entidad")),
            "n": nombre,
            "m": modalidad,
            "t": normalize(r.get("tipo_de_contrato")) or "No Especificado",
            "v": int(valor or 0),
            "rup": modalidad not in SIN_RUP,
            "dl": dias_entre(corte, date.fromisoformat(f)),
            "f": f,
            "tm": detectar_temas(texto),
            "pilares": detectar_pilares(texto),
            "u": u,
        })
    return out


def _dedupe(records: list[dict]) -> list[dict]:
    unicos: dict[str, dict] = {}
    for r in records:
        unicos[r["u"] or f"{r['e']}|{r['n']}|{r['f']}"] = r
    return list(unicos.values())


def _guardar(records: list[dict], corte: date) -> int:
    # Reemplaza el corte: la fuente es un snapshot, no un histórico acumulado.
    SecopProceso.query.filter_by(corte=corte).delete()
    for r in records:
        db.session.add(SecopProceso(
            entidad=r["e"],
            departamento=r["d"],
            ciudad=r["c"],
            nombre=r["n"],
            modalidad=r["m"],
            tipo_contrato=r["t"],
            valor=r["v"],
            requiere_rup=r["rup"],
            fecha_limite=date.fromisoformat(r["f"]),
            corte=corte,
            temas=r["tm"],
            pilares=r["pilares"],
            url=r["u"],
        ))
    db.session.commit()
    return len(records)


def actualizar_secop(corte: date | None = None) -> dict:
    """Descarga, valida y persiste los procesos SECOP II vigentes para el corte."""
    corte = corte or hoy_bogota()
    corte_ini = f"{corte.isoformat()}T00:00:00.000"

    params = {
        "$where": (
            "fase = 'Presentación de oferta'"
            " AND estado_de_apertura_del_proceso = 'Abierto'"
            f" AND fecha_de_recepcion_de >= '{corte_ini}'"
        ),
        "$order": "fecha_de_recepcion_de ASC",
    }

    try:
        raw_rows = _fetch_paginated(params)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
        raise SecopError(f"No se pudo consultar datos.gov.co: {exc}") from exc

    records = _normalizar_registros(raw_rows, corte)
    records = _dedupe(records)

    errores = validar(records)
    if errores:
        raise SecopError(
            f"Validación falló: {len(errores)} errores. No se publican datos corruptos. "
            f"{'; '.join(errores[:5])}"
        )

    total = _guardar(records, corte)
    existente = SecopCorte.query.filter_by(corte=corte).first()
    if existente:
        existente.total = total
        existente.generado_at = datetime.now(timezone.utc).replace(tzinfo=None)
    else:
        db.session.add(SecopCorte(corte=corte, total=total))
    db.session.commit()

    return {
        "total": total,
        "corte": corte.isoformat(),
        "corte_legible": f"{corte.day} {['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic'][corte.month - 1]} {corte.year}",
        "generado": hoy_bogota().isoformat(),
    }
