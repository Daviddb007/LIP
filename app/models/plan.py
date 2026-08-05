"""
Modelo de datos configurable para alinear la participación ciudadana
con CUALQUIER instrumento de planeación (plan de gobierno nacional,
departamental, municipal, o de una organización).

Jerarquía:
    Plan
     └─ Pilar
         └─ LineaEstrategica
             └─ Componente
                 └─ Objetivo
                     └─ Indicador
"""
from __future__ import annotations

from datetime import datetime, timezone

from app import db


class Plan(db.Model):
    """Plan estratégico configurable (PND, plan de gobierno, etc.)."""

    __tablename__ = "planes"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    version = db.Column(db.String(50), nullable=False, default="1.0")
    ambito = db.Column(
        db.String(30), nullable=False, default="nacional"
    )  # nacional | departamental | municipal | organizacional
    vigencia_inicio = db.Column(db.Date, nullable=False)
    vigencia_fin = db.Column(db.Date, nullable=True)
    activo = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    pilares = db.relationship(
        "Pilar",
        backref="plan",
        order_by="Pilar.orden",
        cascade="all, delete-orphan",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<Plan {self.nombre} v{self.version}>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "version": self.version,
            "ambito": self.ambito,
            "vigencia_inicio": self.vigencia_inicio.isoformat(),
            "vigencia_fin": self.vigencia_fin.isoformat() if self.vigencia_fin else None,
            "activo": self.activo,
        }


class Pilar(db.Model):
    """Pilar del plan estratégico."""

    __tablename__ = "pilares"

    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey("planes.id"), nullable=False)
    nombre = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(220), nullable=False, index=True)
    tipo = db.Column(
        db.String(20), nullable=False, default="tematico"
    )  # fundacional | tematico
    orden = db.Column(db.Integer, nullable=False, default=0)
    descripcion = db.Column(db.Text, nullable=True)
    activo = db.Column(db.Boolean, default=True, nullable=False)

    lineas = db.relationship(
        "LineaEstrategica",
        backref="pilar",
        order_by="LineaEstrategica.orden",
        cascade="all, delete-orphan",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<Pilar {self.orden}. {self.nombre}>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "plan_id": self.plan_id,
            "nombre": self.nombre,
            "slug": self.slug,
            "tipo": self.tipo,
            "orden": self.orden,
            "descripcion": self.descripcion,
            "activo": self.activo,
        }


class LineaEstrategica(db.Model):
    """Línea estratégica dentro de un pilar."""

    __tablename__ = "lineas_estrategicas"

    id = db.Column(db.Integer, primary_key=True)
    pilar_id = db.Column(db.Integer, db.ForeignKey("pilares.id"), nullable=False)
    nombre = db.Column(db.String(200), nullable=False)
    orden = db.Column(db.Integer, nullable=False, default=0)
    descripcion = db.Column(db.Text, nullable=True)

    componentes = db.relationship(
        "Componente",
        backref="linea",
        cascade="all, delete-orphan",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<LineaEstrategica {self.nombre}>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "pilar_id": self.pilar_id,
            "nombre": self.nombre,
            "orden": self.orden,
            "descripcion": self.descripcion,
        }


class Componente(db.Model):
    """Componente dentro de una línea estratégica."""

    __tablename__ = "componentes"

    id = db.Column(db.Integer, primary_key=True)
    linea_id = db.Column(
        db.Integer, db.ForeignKey("lineas_estrategicas.id"), nullable=False
    )
    nombre = db.Column(db.String(200), nullable=False)

    objetivos = db.relationship(
        "Objetivo",
        backref="componente",
        cascade="all, delete-orphan",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<Componente {self.nombre}>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "linea_id": self.linea_id,
            "nombre": self.nombre,
        }


class Objetivo(db.Model):
    """Objetivo dentro de un componente."""

    __tablename__ = "objetivos"

    id = db.Column(db.Integer, primary_key=True)
    componente_id = db.Column(
        db.Integer, db.ForeignKey("componentes.id"), nullable=False
    )
    nombre = db.Column(db.String(200), nullable=False)
    ods = db.Column(db.String(10), nullable=True)  # ODS asociado

    indicadores = db.relationship(
        "Indicador",
        backref="objetivo",
        cascade="all, delete-orphan",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<Objetivo {self.nombre}>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "componente_id": self.componente_id,
            "nombre": self.nombre,
            "ods": self.ods,
        }


class Indicador(db.Model):
    """Indicador dentro de un objetivo."""

    __tablename__ = "indicadores"

    id = db.Column(db.Integer, primary_key=True)
    objetivo_id = db.Column(db.Integer, db.ForeignKey("objetivos.id"), nullable=False)
    nombre = db.Column(db.String(200), nullable=False)
    meta = db.Column(db.String(100), nullable=True)
    unidad = db.Column(db.String(50), nullable=True)

    def __repr__(self) -> str:
        return f"<Indicador {self.nombre}>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "objetivo_id": self.objetivo_id,
            "nombre": self.nombre,
            "meta": self.meta,
            "unidad": self.unidad,
        }
