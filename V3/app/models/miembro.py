"""Modelo de miembro del equipo para la página Nosotros."""
from __future__ import annotations

from datetime import datetime

from app import db


class MiembroEquipo(db.Model):
    """Miembro del equipo directivo/operativo."""

    __tablename__ = "miembros_equipo"
    __table_args__ = (
        db.Index("idx_miembro_orden", "orden"),
        db.Index("idx_miembro_activo", "activo"),
    )

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    cargo = db.Column(db.String(200), nullable=True)
    descripcion = db.Column(db.Text, nullable=True)
    foto_url = db.Column(db.String(500), nullable=True)
    orden = db.Column(db.Integer, nullable=False, default=0)
    activo = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<MiembroEquipo {self.nombre}>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "cargo": self.cargo,
            "descripcion": self.descripcion,
            "foto_url": self.foto_url,
            "orden": self.orden,
            "activo": self.activo,
        }

    @classmethod
    def activos(cls):
        return cls.query.filter_by(activo=True).order_by(cls.orden).all()
