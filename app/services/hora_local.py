"""Hora local de Colombia (America/Bogota, UTC-5).

El servidor puede correr en UTC; cualquier operación que necesite la fecha/hora
"de hoy en Bogotá" (p.ej. el corte SECOP, vencimientos, "dl") debe usar esto en
vez de date.today()/datetime.now() del sistema, para no adelantar/atrasar un día.
"""
from __future__ import annotations

from datetime import date, datetime
from zoneinfo import ZoneInfo

_BOGOTA = ZoneInfo("America/Bogota")


def hoy_bogota() -> date:
    return datetime.now(_BOGOTA).date()


def ahora_bogota() -> datetime:
    return datetime.now(_BOGOTA)
