"""Servicio de integración para el ecosistema de socios y webhooks.

Maneja el envío de eventos a webhooks registrados y expone el catálogo
de socios del ecosistema de inteligencia pública.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any
from urllib import request as http_request
from urllib.error import URLError

from app import db
from app.models.webhook import Webhook

logger = logging.getLogger(__name__)


def dispatch(evento: str, datos: dict) -> list[dict]:
    """Despacha un evento a todos los webhooks activos para ese tipo de evento."""
    resultados: list[dict] = []
    webhooks = Webhook.activos_por_evento(evento)

    for wh in webhooks:
        resultado = _enviar(wh, evento, datos)
        wh.ultimo_envio = datetime.now(timezone.utc)
        wh.ultimo_estado = resultado['status']
        db.session.commit()
        resultados.append(resultado)

    return resultados


def _enviar(webhook: Webhook, evento: str, datos: dict) -> dict:
    """Envía un payload JSON al webhook destino con cabecera de evento."""
    payload = json.dumps({
        'evento': evento,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'data': datos,
    }).encode('utf-8')

    try:
        req = http_request.Request(
            webhook.url,
            data=payload,
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'ConstruyamosColombia-Webhook/1.0',
                'X-Webhook-Event': evento,
            },
            method='POST',
        )

        with http_request.urlopen(req, timeout=10) as resp:
            status = resp.status
            logger.info(f'Webhook {webhook.nombre} → {status}')
            return {'webhook_id': webhook.id, 'nombre': webhook.nombre, 'status': status, 'exito': True}
    except URLError as e:
        logger.error(f'Webhook {webhook.nombre} error: {e}')
        return {'webhook_id': webhook.id, 'nombre': webhook.nombre, 'status': 0, 'exito': False, 'error': str(e)}


PARTNERS: list[dict] = [
    {
        'nombre': 'Ministerio de Tecnologías de la Información',
        'sigla': 'Mintic',
        'tipo': 'Ministerio',
        'descripcion': 'Integración para digitalización de trámites y gobierno digital.',
        'icono': 'bi-laptop',
        'color': '#2563eb',
        'estado': 'disponible',
    },
    {
        'nombre': 'Departamento Nacional de Planeación',
        'sigla': 'DNP',
        'tipo': 'Departamento Administrativo',
        'descripcion': 'Conexión con el Sistema de Planeación Nacional para armonización de políticas.',
        'icono': 'bi-diagram-3',
        'color': '#7c3aed',
        'estado': 'disponible',
    },
    {
        'nombre': 'Gobernación de Antioquia',
        'sigla': 'Gobernación',
        'tipo': 'Gobernación',
        'descripcion': 'Portal territorial de participación ciudadana con SRIE.',
        'icono': 'bi-building',
        'color': '#10b981',
        'estado': 'piloto',
    },
    {
        'nombre': 'Universidad Nacional de Colombia',
        'sigla': 'UNAL',
        'tipo': 'Universidad',
        'descripcion': 'Investigación académica y laboratorio de innovación pública.',
        'icono': 'bi-book',
        'color': '#f59e0b',
        'estado': 'disponible',
    },
    {
        'nombre': 'Programa de las Naciones Unidas para el Desarrollo',
        'sigla': 'PNUD',
        'tipo': 'Cooperación Internacional',
        'descripcion': 'Monitoreo de ODS y políticas públicas con enfoque de desarrollo sostenible.',
        'icono': 'bi-globe2',
        'color': '#06b6d4',
        'estado': 'potencial',
    },
    {
        'nombre': 'Alcaldía de Medellín',
        'sigla': 'Alcaldía',
        'tipo': 'Alcaldía',
        'descripcion': 'Observatorio local de participación ciudadana alimentado por SRIE.',
        'icono': 'bi-geo-alt',
        'color': '#ec4899',
        'estado': 'piloto',
    },
    {
        'nombre': 'Centro de Pensamiento Estratégico',
        'sigla': 'CPE',
        'tipo': 'Centro de Pensamiento',
        'descripcion': 'Análisis de tendencias y generación de informes basados en evidencia.',
        'icono': 'bi-lightbulb',
        'color': '#f97316',
        'estado': 'disponible',
    },
    {
        'nombre': 'Corporación Andina de Fomento',
        'sigla': 'CAF',
        'tipo': 'Cooperación Internacional',
        'descripcion': 'Financiamiento de proyectos de innovación pública basados en datos SRIE.',
        'icono': 'bi-cash-stack',
        'color': '#14b8a6',
        'estado': 'potencial',
    },
]
