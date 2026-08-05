"""Helpers de base de datos para compatibilidad PostgreSQL/SQLite.

Funciones como date_trunc son específicas de PostgreSQL.
Estos helpers retornan la expresión SQL correcta según el dialecto.
"""
from __future__ import annotations

from app import db
from sqlalchemy import func


def date_trunc(part: str, column) -> func:
    """date_trunc compatible con SQLite y PostgreSQL.

    SQLite no tiene date_trunc nativo. Usamos strftime como alternativa.
    """
    dialect = db.engine.dialect.name
    if dialect == "sqlite":
        if part == "month":
            return func.strftime("%Y-%m-01", column)
        elif part == "day":
            return func.strftime("%Y-%m-%d", column)
        return func.strftime("%Y-%m-%d", column)
    return func.date_trunc(part, column)
