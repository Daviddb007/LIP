"""Modelo de organización multi-tenant para SaaS."""
from __future__ import annotations

from datetime import datetime
import secrets

from app import db


class Organizacion(db.Model):
    """Organización cliente del SaaS multi-tenant."""

    __tablename__ = "organizaciones"
    __table_args__ = (
        db.Index("idx_org_nombre", "nombre"),
        db.Index("idx_org_slug", "slug"),
    )

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    plan = db.Column(db.String(50), nullable=False, default="gratuito")
    activo = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    config = db.Column(db.Text, nullable=True, default="{}")

    TIPOS = [
        ("ministerio", "Ministerio"),
        ("gobernacion", "Gobernación"),
        ("alcaldia", "Alcaldía"),
        ("universidad", "Universidad"),
        ("centro_pensamiento", "Centro de Pensamiento"),
        ("ong", "ONG"),
        ("cooperacion", "Cooperación Internacional"),
        ("empresa", "Empresa Privada"),
    ]

    PLANES = [
        ("gratuito", "Gratuito - 100 participaciones/mes"),
        ("basico", "Básico - 1.000 participaciones/mes"),
        ("profesional", "Profesional - 10.000 participaciones/mes"),
        ("empresarial", "Empresarial - Ilimitado"),
    ]

    def __repr__(self) -> str:
        return f"<Organizacion {self.nombre}>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "slug": self.slug,
            "tipo": self.tipo,
            "plan": self.plan,
            "activo": self.activo,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def por_slug(cls, slug: str):
        return cls.query.filter_by(slug=slug, activo=True).first()

    @staticmethod
    def generar_slug(nombre: str) -> str:
        slug = nombre.lower().replace(" ", "-").replace("ñ", "n")[:80]
        slug = "".join(c for c in slug if c.isalnum() or c == "-")
        if Organizacion.query.filter_by(slug=slug).first():
            slug += f"-{secrets.token_hex(3)}"
        return slug
