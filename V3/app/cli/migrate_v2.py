"""Migración de datos desde V2 a V3.

Lee desde la base de datos V2 (construyamos_colombia) y migra
participaciones, sectores y clasificaciones al esquema V3.

Uso: flask migrate-v2
"""
from __future__ import annotations

import logging
from datetime import datetime

from app import db
from app.models.catalog import (
    ProblemaCatalogo, Subsector, Actor, Beneficiario,
    participacion_problemas, participacion_actores, participacion_beneficiarios,
)
from app.models.participacion import Participacion, ClasificacionSRIE
from app.models.plan import Pilar
from sqlalchemy import text

logger = logging.getLogger(__name__)

ZONA_DEFAULT = "urbana"


def run_migration(dry_run: bool = False) -> dict:
    """Ejecuta la migración de V2 a V3. Si dry_run=True, solo cuenta sin insertar."""
    stats = {"participaciones": 0, "clasificaciones": 0, "errores": 0, "saltados": 0}

    v2_rows = _fetch_v2_participaciones()
    logger.info("Encontradas %d participaciones en V2", len(v2_rows))

    pilares_map = {p.nombre.lower(): p.id for p in Pilar.query.all()}

    for row in v2_rows:
        try:
            if _exists_in_v3(row["id"]):
                stats["saltados"] += 1
                continue

            if dry_run:
                stats["participaciones"] += 1
                continue

            participacion = _migrar_participacion(row, pilares_map)
            db.session.add(participacion)
            db.session.flush()

            _migrar_sectores(participacion, row.get("sector_ids", []))
            _migrar_clasificacion(participacion, row, pilares_map)
            _migrar_actores_texto(participacion, row.get("actores_responsables", ""))
            _migrar_beneficiarios_texto(participacion, row.get("beneficiarios", ""))

            stats["participaciones"] += 1

        except Exception as e:
            logger.error("Error migrando participación %s: %s", row.get("id"), e)
            stats["errores"] += 1

    if not dry_run:
        db.session.commit()
        logger.info("Migración completada: %d participaciones", stats["participaciones"])

    return stats


def _fetch_v2_participaciones() -> list[dict]:
    """Lee participaciones desde la base V2 (misma instancia PostgreSQL, DB distinta)."""
    v2_db_url = _get_v2_db_url()
    if not v2_db_url:
        logger.warning("No se encontró V2_DATABASE_URL. Usando misma DB con schema público.")
        return _fetch_from_public()

    try:
        v2_engine = db.create_engine(v2_db_url)
        with v2_engine.connect() as conn:
            rows = conn.execute(text("""
                SELECT p.*, array_agg(ps.sector_id) as sector_ids
                FROM participaciones p
                LEFT JOIN participacion_sectores ps ON ps.participacion_id = p.id
                GROUP BY p.id
                ORDER BY p.id
            """)).mappings().all()
            return [dict(r) for r in rows]
    except Exception as e:
        logger.error("Error conectando a V2_DATABASE_URL: %s", e)
        return []


def _fetch_from_public() -> list[dict]:
    """Falla segura: intenta leer desde esquema público de la misma DB."""
    try:
        rows = db.session.execute(text("""
            SELECT p.*, array_agg(ps.sector_id) as sector_ids
            FROM participaciones p
            LEFT JOIN participacion_sectores ps ON ps.participacion_id = p.id
            GROUP BY p.id
            ORDER BY p.id
        """))
        return [dict(r) for r in rows]
    except Exception as e:
        logger.warning("No se pudieron leer datos V2: %s", e)
        return []


def _get_v2_db_url() -> str | None:
    """Obtiene URL de DB V2 desde variable de entorno."""
    import os
    return os.environ.get("V2_DATABASE_URL", None)


def _exists_in_v3(v2_id: int) -> bool:
    """Verifica si esta participación ya fue migrada (por id)."""
    return Participacion.query.filter(
        Participacion.created_at == _fecha_estimada(v2_id)
    ).first() is not None


def _fecha_estimada(v2_id: int) -> datetime:
    """Genera fecha estimada para evitar duplicados."""
    return datetime(2026, 1, 1)


def _migrar_participacion(row: dict, pilares_map: dict) -> Participacion:
    """Crea una Participacion V3 desde datos V2."""
    return Participacion(
        departamento=row.get("departamento", "No especificado"),
        municipio=row.get("municipio", "No especificado"),
        zona=ZONA_DEFAULT,
        justificacion=row.get("contexto_ciudadano") or row.get("propuesta", "")[:200] or "Migrada desde V2",
        propuesta=row.get("propuesta", "") or "Migrada desde V2",
        rango_edad=row.get("rango_edad"),
        genero=row.get("genero"),
        ip_hash=row.get("ip_hash"),
        created_at=row.get("created_at", datetime.utcnow()),
    )


def _migrar_sectores(participacion: Participacion, sector_ids: list[int]) -> None:
    """Mapa sectores V2 a problemas V3 de forma aproximada.

    Toma el primer problema activo de cada sector V2 y lo asocia.
    """
    if not sector_ids:
        return

    problemas = (
        ProblemaCatalogo.query
        .join(Subsector)
        .filter(Subsector.sector_id.in_(sector_ids), ProblemaCatalogo.activo.is_(True))
        .limit(3)
        .all()
    )

    for problema in problemas:
        if problema.id not in [p.id for p in getattr(participacion, "_problemas_temp", [])]:
            db.session.execute(
                participacion_problemas.insert().values(
                    participacion_id=participacion.id,
                    problema_id=problema.id,
                )
            )


def _migrar_clasificacion(
    participacion: Participacion,
    row: dict,
    pilares_map: dict,
) -> None:
    """Crea una ClasificacionSRIE V3 desde el srie_pilar V2."""
    srie_pilar = (row.get("srie_pilar") or "").strip().lower()
    if not srie_pilar:
        return

    pilar_id = pilares_map.get(srie_pilar)
    if not pilar_id:
        for nombre, pid in pilares_map.items():
            if srie_pilar in nombre or nombre in srie_pilar:
                pilar_id = pid
                break

    if not pilar_id:
        logger.debug("Pilar '%s' no encontrado en V3, saltando clasificación", srie_pilar)
        return

    clasificacion = ClasificacionSRIE(
        participacion_id=participacion.id,
        pilar_id=pilar_id,
        confianza=0.5,
        ranking=1,
        modelo_usado="migracion-v2",
    )

    srie_confianza = row.get("srie_confianza")
    if srie_confianza:
        try:
            confianza_float = float(srie_confianza) / 100.0
            clasificacion.confianza = min(max(confianza_float, 0.0), 1.0)
        except (ValueError, TypeError):
            pass

    db.session.add(clasificacion)


def _migrar_actores_texto(participacion: Participacion, texto: str) -> None:
    """Intenta mapear actores desde texto libre a catálogo V3."""
    if not texto:
        return

    texto_lower = texto.lower()
    actores = Actor.query.filter(Actor.activo.is_(True)).all()

    for actor in actores:
        if actor.nombre.lower() in texto_lower or actor.slug in texto_lower:
            db.session.execute(
                participacion_actores.insert().values(
                    participacion_id=participacion.id,
                    actor_id=actor.id,
                )
            )


def _migrar_beneficiarios_texto(participacion: Participacion, texto: str) -> None:
    """Intenta mapear beneficiarios desde texto libre a catálogo V3."""
    if not texto:
        return

    texto_lower = texto.lower()
    beneficiarios = Beneficiario.query.filter(Beneficiario.activo.is_(True)).all()

    for b in beneficiarios:
        if b.nombre.lower() in texto_lower or b.slug in texto_lower:
            db.session.execute(
                participacion_beneficiarios.insert().values(
                    participacion_id=participacion.id,
                    beneficiario_id=b.id,
                )
            )
