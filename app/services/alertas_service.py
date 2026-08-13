"""Servicio de alertas operativas del Centro Nacional de Inteligencia.

Genera alertas accionables a partir de reglas de negocio:
  - clasificaciones SRIE con confianza baja
  - picos de participación vs la media reciente
  - sectores con participación ciudadana pero sin política asociada
  - webhooks con último envío fallido
  - audios de grupos focales pendientes de transcripción
"""
from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Any

from app import db
from app.models.catalog import Sector, Subsector, ProblemaCatalogo, participacion_problemas
from app.models.participacion import Participacion, ClasificacionSRIE
from app.models.politica import Politica
from app.models.webhook import Webhook
from sqlalchemy import func

UMBRAL_CONFIANZA = 0.5
UMBRAL_PICO = 2.0
VENTANA_PICO_DIAS = 7


def obtener_alertas() -> list[dict[str, Any]]:
    alertas: list[dict[str, Any]] = []
    alertas.extend(_alertas_confianza_baja())
    alertas.extend(_alertas_pico_participacion())
    alertas.extend(_alertas_sectores_sin_politica())
    alertas.extend(_alertas_webhooks_fallidos())
    alertas.extend(_alertas_transcripciones_pendientes())
    return sorted(alertas, key=lambda a: {"alta": 0, "media": 1, "baja": 2}[a["severidad"]])


def _alertas_confianza_baja() -> list[dict[str, Any]]:
    ahora = datetime.now(timezone.utc).replace(tzinfo=None)
    limite = ahora - timedelta(days=7)
    total = (
        db.session.query(func.count(ClasificacionSRIE.id))
        .filter(ClasificacionSRIE.confianza < UMBRAL_CONFIANZA)
        .filter(ClasificacionSRIE.created_at >= limite)
        .scalar()
        or 0
    )
    if total == 0:
        return []
    return [{
        "severidad": "media",
        "titulo": f"{total} clasificación(es) con confianza baja",
        "detalle": f"Confianza < {UMBRAL_CONFIANZA} en los últimos 7 días. Revisar el diccionario de keywords del motor SRIE.",
        "enlace": "/admin/clasificaciones",
    }]


def _alertas_pico_participacion() -> list[dict[str, Any]]:
    ahora = datetime.now(timezone.utc).replace(tzinfo=None)
    hoy_inicio = ahora.replace(hour=0, minute=0, second=0, microsecond=0)
    inicio_ventana = hoy_inicio - timedelta(days=VENTANA_PICO_DIAS)

    hoy = Participacion.query.filter(Participacion.created_at >= hoy_inicio).count()
    previos = Participacion.query.filter(
        Participacion.created_at >= inicio_ventana,
        Participacion.created_at < hoy_inicio,
    ).count()
    media = previos / VENTANA_PICO_DIAS if VENTANA_PICO_DIAS else 0
    if hoy == 0 or media == 0 or hoy <= media * UMBRAL_PICO:
        return []
    return [{
        "severidad": "baja",
        "titulo": "Pico de participación detectado",
        "detalle": f"{hoy} participaciones hoy vs media de {media:.1f}/día en la última semana.",
        "enlace": "/admin/participaciones",
    }]


def _alertas_sectores_sin_politica() -> list[dict[str, Any]]:
    sectores_con_participacion = (
        db.session.query(Sector.nombre)
        .join(Subsector, Subsector.sector_id == Sector.id)
        .join(ProblemaCatalogo, ProblemaCatalogo.subsector_id == Subsector.id)
        .join(participacion_problemas, participacion_problemas.c.problema_id == ProblemaCatalogo.id)
        .join(Participacion, Participacion.id == participacion_problemas.c.participacion_id)
        .group_by(Sector.nombre)
        .all()
    )
    nombres = [s[0] for s in sectores_con_participacion]
    if not nombres:
        return []

    politicas_por_sector: set[str] = set()
    for p in Politica.query.filter_by(activo=True).all():
        if p.sector:
            politicas_por_sector.add(p.sector.nombre)

    sin_politica = [n for n in nombres if n not in politicas_por_sector]
    if not sin_politica:
        return []
    return [{
        "severidad": "media",
        "titulo": "Sectores con participación sin política",
        "detalle": ", ".join(sin_politica[:6]) + ("..." if len(sin_politica) > 6 else ""),
        "enlace": "/admin/planes",
    }]


def _alertas_webhooks_fallidos() -> list[dict[str, Any]]:
    fallidos = (
        Webhook.query.filter(
            Webhook.activo.is_(True),
            Webhook.ultimo_estado.isnot(None),
            Webhook.ultimo_estado >= 400,
        ).all()
    )
    if not fallidos:
        return []
    return [{
        "severidad": "alta",
        "titulo": f"{len(fallidos)} webhook(s) con envío fallido",
        "detalle": ", ".join(f"{w.nombre} (HTTP {w.ultimo_estado})" for w in fallidos[:5]),
        "enlace": "/ecosistema",
    }]


def _alertas_transcripciones_pendientes() -> list[dict[str, Any]]:
    try:
        from app.models.focal import AudioFocal
    except ImportError:
        return []
    pendientes = AudioFocal.query.filter(AudioFocal.estado == "pendiente").count()
    errores = AudioFocal.query.filter(AudioFocal.estado == "error").count()
    if pendientes == 0 and errores == 0:
        return []
    return [{
        "severidad": "alta" if errores else "media",
        "titulo": "Grupos focales: transcripciones pendientes",
        "detalle": f"{pendientes} pendiente(s) y {errores} en error. Revisar el worker (RQ).",
        "enlace": "/admin/focales/sesiones",
    }]
