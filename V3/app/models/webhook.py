"""Modelo de webhook para integraciones del ecosistema."""
from __future__ import annotations

from datetime import datetime

from app import db


class Webhook(db.Model):
    """Webhook registrado para recibir eventos del ecosistema."""

    __tablename__ = "webhooks"
    __table_args__ = (
        db.Index("idx_webhook_evento", "evento"),
    )

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    evento = db.Column(db.String(50), nullable=False)
    activo = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ultimo_envio = db.Column(db.DateTime, nullable=True)
    ultimo_estado = db.Column(db.Integer, nullable=True)

    def __repr__(self) -> str:
        return f"<Webhook {self.nombre} ({self.evento})>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "url": self.url,
            "evento": self.evento,
            "activo": self.activo,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "ultimo_envio": self.ultimo_envio.isoformat() if self.ultimo_envio else None,
            "ultimo_estado": self.ultimo_estado,
        }

    @classmethod
    def activos_por_evento(cls, evento: str):
        return cls.query.filter_by(evento=evento, activo=True).all()
