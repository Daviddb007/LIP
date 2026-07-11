"""Modelo de política pública para la Biblioteca.

Almacena documentos de política pública con metadatos completos
(sector, objetivos, normatividad, presupuesto, ODS, etc.).
"""
from __future__ import annotations

from datetime import datetime

from app import db


class Politica(db.Model):
    """Documento de política pública con metadatos completos."""

    __tablename__ = "politicas"
    __table_args__ = (
        db.Index("idx_politica_titulo", "titulo"),
        db.Index("idx_politica_sector", "sector_id"),
        db.Index("idx_politica_activo", "activo"),
        db.Index("idx_politica_estado", "estado"),
    )

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(300), nullable=False)
    sector_id = db.Column(db.Integer, db.ForeignKey("catalogo_sectores.id"), nullable=True)
    resumen_ejecutivo = db.Column(db.Text, nullable=False)
    problema = db.Column(db.Text, nullable=True)
    objetivos = db.Column(db.Text, nullable=True)
    poblacion_objetivo = db.Column(db.String(300), nullable=True)
    normatividad = db.Column(db.Text, nullable=True)
    cronologia = db.Column(db.Text, nullable=True)
    entidades_responsables = db.Column(db.String(500), nullable=True)
    indicadores = db.Column(db.Text, nullable=True)
    presupuesto = db.Column(db.String(200), nullable=True)
    estado = db.Column(db.String(50), nullable=False, default="Activa")
    documentos = db.Column(db.Text, nullable=True)
    ods_relacionados = db.Column(db.String(200), nullable=True)
    alcance = db.Column(db.String(100), nullable=True)
    activo = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    sector = db.relationship("Sector", foreign_keys=[sector_id], lazy="joined")

    def __repr__(self) -> str:
        return f"<Politica {self.titulo[:50]}>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "titulo": self.titulo,
            "sector_id": self.sector_id,
            "sector_nombre": self.sector.nombre if self.sector else "",
            "resumen_ejecutivo": self.resumen_ejecutivo,
            "problema": self.problema,
            "objetivos": self.objetivos,
            "poblacion_objetivo": self.poblacion_objetivo,
            "normatividad": self.normatividad,
            "cronologia": self.cronologia,
            "entidades_responsables": self.entidades_responsables,
            "indicadores": self.indicadores,
            "presupuesto": self.presupuesto,
            "estado": self.estado,
            "documentos": self.documentos,
            "ods_relacionados": self.ods_relacionados,
            "alcance": self.alcance,
            "activo": self.activo,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
