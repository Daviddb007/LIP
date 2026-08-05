"""
Modelos de catálogo: Sector, Subsector, Problema, Actor, Beneficiario.

Jerarquía 3 niveles:
    Sector → Subsector → Problema

M:N junction tables para actores y beneficiarios en participaciones.
"""
from __future__ import annotations

from datetime import datetime

from app import db


# ---------------------------------------------------------------------------
# Junction tables (M:N)
# ---------------------------------------------------------------------------

participacion_problemas = db.Table(
    "participacion_problemas",
    db.Column("participacion_id", db.Integer, db.ForeignKey("participaciones.id"), primary_key=True),
    db.Column("problema_id", db.Integer, db.ForeignKey("catalogo_problemas.id"), primary_key=True),
    db.Index("idx_part_prob_participacion", "participacion_id"),
    db.Index("idx_part_prob_problema", "problema_id"),
)

participacion_actores = db.Table(
    "participacion_actores",
    db.Column("participacion_id", db.Integer, db.ForeignKey("participaciones.id"), primary_key=True),
    db.Column("actor_id", db.Integer, db.ForeignKey("catalogo_actores.id"), primary_key=True),
    db.Index("idx_part_act_participacion", "participacion_id"),
    db.Index("idx_part_act_actor", "actor_id"),
)

participacion_beneficiarios = db.Table(
    "participacion_beneficiarios",
    db.Column("participacion_id", db.Integer, db.ForeignKey("participaciones.id"), primary_key=True),
    db.Column("beneficiario_id", db.Integer, db.ForeignKey("catalogo_beneficiarios.id"), primary_key=True),
    db.Index("idx_part_bene_participacion", "participacion_id"),
    db.Index("idx_part_bene_beneficiario", "beneficiario_id"),
)


# ---------------------------------------------------------------------------
# Sector (nivel 1)
# ---------------------------------------------------------------------------

class Sector(db.Model):
    """Sector económico o temático (nivel 1 de la jerarquía)."""

    __tablename__ = "catalogo_sectores"
    __table_args__ = (
        db.Index("idx_sector_activo", "activo"),
    )

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    slug = db.Column(db.String(120), nullable=False, unique=True, index=True)
    icono = db.Column(db.String(50), nullable=False, default="folder")
    color = db.Column(db.String(20), nullable=False, default="#3B82F6")
    orden = db.Column(db.Integer, nullable=False, default=0)
    activo = db.Column(db.Boolean, default=True, nullable=False)

    subsectores = db.relationship(
        "Subsector", backref="sector", order_by="Subsector.orden",
        cascade="all, delete-orphan", lazy="select",
    )

    def __repr__(self) -> str:
        return f"<Sector {self.nombre}>"

    def to_dict(self) -> dict:
        return {
            "id": self.id, "nombre": self.nombre, "slug": self.slug,
            "icono": self.icono, "color": self.color, "orden": self.orden,
            "activo": self.activo,
        }


# ---------------------------------------------------------------------------
# Subsector (nivel 2)
# ---------------------------------------------------------------------------

class Subsector(db.Model):
    """Subsector dentro de un sector (nivel 2)."""

    __tablename__ = "catalogo_subsectores"
    __table_args__ = (
        db.Index("idx_subsector_sector", "sector_id"),
    )

    id = db.Column(db.Integer, primary_key=True)
    sector_id = db.Column(db.Integer, db.ForeignKey("catalogo_sectores.id"), nullable=False)
    nombre = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(170), nullable=False, index=True)
    icono = db.Column(db.String(50), nullable=False, default="folder2")
    orden = db.Column(db.Integer, nullable=False, default=0)
    activo = db.Column(db.Boolean, default=True, nullable=False)

    problemas = db.relationship(
        "ProblemaCatalogo", backref="subsector", order_by="ProblemaCatalogo.orden",
        cascade="all, delete-orphan", lazy="select",
    )

    def __repr__(self) -> str:
        return f"<Subsector {self.nombre}>"

    def to_dict(self) -> dict:
        return {
            "id": self.id, "sector_id": self.sector_id, "nombre": self.nombre,
            "slug": self.slug, "icono": self.icono, "orden": self.orden,
            "activo": self.activo,
        }


# ---------------------------------------------------------------------------
# Problema (nivel 3) — catálogo de problemas
# ---------------------------------------------------------------------------

class ProblemaCatalogo(db.Model):
    """Problema específico dentro de un subsector (nivel 3)."""

    __tablename__ = "catalogo_problemas"
    __table_args__ = (
        db.Index("idx_problema_cat_subsector", "subsector_id"),
        db.Index("idx_problema_cat_activo", "activo"),
    )

    id = db.Column(db.Integer, primary_key=True)
    subsector_id = db.Column(db.Integer, db.ForeignKey("catalogo_subsectores.id"), nullable=False)
    nombre = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(220), nullable=False, index=True)
    descripcion = db.Column(db.Text, nullable=True)
    icono = db.Column(db.String(50), nullable=False, default="exclamation-circle")
    orden = db.Column(db.Integer, nullable=False, default=0)
    activo = db.Column(db.Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<ProblemaCatalogo {self.nombre}>"

    def to_dict(self) -> dict:
        return {
            "id": self.id, "subsector_id": self.subsector_id, "nombre": self.nombre,
            "slug": self.slug, "descripcion": self.descripcion, "icono": self.icono,
            "orden": self.orden, "activo": self.activo,
        }


# ---------------------------------------------------------------------------
# Actor (quién debería liderar)
# ---------------------------------------------------------------------------

class Actor(db.Model):
    """Actor que podría liderar la solución de un problema."""

    __tablename__ = "catalogo_actores"
    __table_args__ = (
        db.Index("idx_actor_activo", "activo"),
    )

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    slug = db.Column(db.String(120), nullable=False, unique=True, index=True)
    icono = db.Column(db.String(50), nullable=False, default="person")
    orden = db.Column(db.Integer, nullable=False, default=0)
    activo = db.Column(db.Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<Actor {self.nombre}>"

    def to_dict(self) -> dict:
        return {
            "id": self.id, "nombre": self.nombre, "slug": self.slug,
            "icono": self.icono, "orden": self.orden, "activo": self.activo,
        }


# ---------------------------------------------------------------------------
# Beneficiario (a quién beneficia)
# ---------------------------------------------------------------------------

class Beneficiario(db.Model):
    """Grupo beneficiario de una propuesta."""

    __tablename__ = "catalogo_beneficiarios"
    __table_args__ = (
        db.Index("idx_beneficiario_activo", "activo"),
    )

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    slug = db.Column(db.String(120), nullable=False, unique=True, index=True)
    icono = db.Column(db.String(50), nullable=False, default="people")
    orden = db.Column(db.Integer, nullable=False, default=0)
    activo = db.Column(db.Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<Beneficiario {self.nombre}>"

    def to_dict(self) -> dict:
        return {
            "id": self.id, "nombre": self.nombre, "slug": self.slug,
            "icono": self.icono, "orden": self.orden, "activo": self.activo,
        }
