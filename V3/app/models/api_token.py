"""Modelo de token API para autenticación de la API REST pública."""
from __future__ import annotations

from datetime import datetime
import secrets

from app import db


class ApiToken(db.Model):
    """Token de autenticación para la API REST pública."""

    __tablename__ = "api_tokens"
    __table_args__ = (
        db.Index("idx_api_token_token", "token"),
    )

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    token = db.Column(db.String(64), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False, default="lectura")
    activo = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_used_at = db.Column(db.DateTime, nullable=True)

    ROLES = ["lectura", "escritura", "admin"]

    def __repr__(self) -> str:
        return f"<ApiToken {self.nombre} ({self.role})>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "token": self.token,
            "role": self.role,
            "activo": self.activo,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_used_at": self.last_used_at.isoformat() if self.last_used_at else None,
        }

    @classmethod
    def verificar(cls, token_str: str):
        return cls.query.filter_by(token=token_str, activo=True).first()

    @classmethod
    def generar(cls, nombre: str, role: str = "lectura") -> ApiToken:
        token_str = secrets.token_hex(32)
        api_token = cls(nombre=nombre, token=token_str, role=role)
        db.session.add(api_token)
        db.session.commit()
        return api_token
