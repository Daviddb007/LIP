"""Modelo de leads de la línea de consultoría para entidades públicas.

LeadConsultoria: solicitud de diagnóstico / consultoría de municipios,
departamentos y entidades centralizadas.
"""
from __future__ import annotations

from datetime import datetime, timezone

from app import db


def _utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class LeadConsultoria(db.Model):
    __tablename__ = "consultoria_leads"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    entidad = db.Column(db.String(200), nullable=False)
    cargo = db.Column(db.String(120), nullable=True)
    email = db.Column(db.String(160), nullable=False, index=True)
    telefono = db.Column(db.String(40), nullable=False)
    tipo_entidad = db.Column(db.String(60), nullable=False, default="municipio")
    necesidad = db.Column(db.String(160), nullable=True)
    mensaje = db.Column(db.Text, nullable=True)
    creado_at = db.Column(db.DateTime, default=_utcnow, nullable=False, index=True)
    atendido = db.Column(db.Boolean, nullable=False, default=False)

    TIPOS = [
        ("municipio", "Municipio"),
        ("departamento", "Gobernación / Departamento"),
        ("entidad_central", "Entidad centralizada"),
        ("universidad", "Universidad"),
        ("ong", "ONG"),
        ("otra", "Otra"),
    ]
