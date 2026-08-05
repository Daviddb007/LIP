"""
Modelos de participación ciudadana y clasificación SRIE.

Participacion: registro completo de una participación (sin FKs a problemas/actores/beneficiarios).
ClasificacionSRIE: resultado del motor de clasificación (top-3 + ranking + keywords_evidencia).

Las relaciones M:N están en catalog.py (participacion_problemas, participacion_actores, participacion_beneficiarios).
"""
from __future__ import annotations

from datetime import datetime, timezone

from app import db


class Participacion(db.Model):
    """Participación ciudadana completa."""

    __tablename__ = "participaciones"
    __table_args__ = (
        db.Index("idx_part_dept_fecha", "departamento", "created_at"),
        db.Index("idx_part_fecha_desc", "created_at"),
        db.Index("idx_part_municipio", "municipio"),
        db.Index("idx_part_zona", "zona"),
    )

    id = db.Column(db.Integer, primary_key=True)

    # Ubicación
    departamento = db.Column(db.String(100), nullable=False, index=True)
    municipio = db.Column(db.String(100), nullable=False)
    zona = db.Column(db.String(20), nullable=False)  # urbana | rural

    # Texto libre
    justificacion = db.Column(db.Text, nullable=False)
    propuesta = db.Column(db.Text, nullable=False)

    # Contexto demográfico
    rango_edad = db.Column(db.String(10), nullable=True)  # 16-18, 19-25, etc.
    genero = db.Column(db.String(20), nullable=True)  # Masculino | Femenino | Otro | Prefiero no decir

    # Seguridad y auditoría
    ip_hash = db.Column(db.String(64), nullable=True)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), nullable=False, index=True
    )

    # Consentimiento (Ley 1581 de 2012 — habeas data)
    consentimiento_aceptado = db.Column(db.Boolean, nullable=False, default=False)
    consentimiento_version = db.Column(db.String(20), nullable=False, default="2026-01")
    consentimiento_at = db.Column(db.DateTime, nullable=True)
    anonimizada = db.Column(db.Boolean, nullable=False, default=False)

    # Relaciones M:N (definidas en catalog.py)
    # Se importan después de definir Participacion para evitar circular imports
    # Acceso via: participacion.problemas, participacion.actores, participacion.beneficiarios

    # Clasificaciones SRIE (top-3)
    clasificaciones = db.relationship(
        "ClasificacionSRIE",
        backref="participacion",
        order_by="ClasificacionSRIE.ranking",
        cascade="all, delete-orphan",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<Participacion {self.id} - {self.departamento}>"

    def to_dict(self) -> dict:
        from app.models.catalog import participacion_problemas, participacion_actores, participacion_beneficiarios
        from app.models.catalog import ProblemaCatalogo, Actor, Beneficiario

        problemas = ProblemaCatalogo.query.join(
            participacion_problemas,
            participacion_problemas.c.problema_id == ProblemaCatalogo.id,
        ).filter(participacion_problemas.c.participacion_id == self.id).all()

        actores = Actor.query.join(
            participacion_actores,
            participacion_actores.c.actor_id == Actor.id,
        ).filter(participacion_actores.c.participacion_id == self.id).all()

        beneficiarios = Beneficiario.query.join(
            participacion_beneficiarios,
            participacion_beneficiarios.c.beneficiario_id == Beneficiario.id,
        ).filter(participacion_beneficiarios.c.participacion_id == self.id).all()

        return {
            "id": self.id,
            "departamento": self.departamento,
            "municipio": self.municipio,
            "zona": self.zona,
            "justificacion": self.justificacion,
            "propuesta": self.propuesta,
            "rango_edad": self.rango_edad,
            "genero": self.genero,
            "problemas": [p.to_dict() for p in problemas],
            "actores": [a.to_dict() for a in actores],
            "beneficiarios": [b.to_dict() for b in beneficiarios],
            "clasificaciones": [c.to_dict() for c in self.clasificaciones],
            "created_at": self.created_at.isoformat(),
        }

    def to_admin_dict(self) -> dict:
        data = self.to_dict()
        data["ip_hash"] = self.ip_hash
        data["consentimiento_aceptado"] = self.consentimiento_aceptado
        data["consentimiento_version"] = self.consentimiento_version
        data["consentimiento_at"] = self.consentimiento_at.isoformat() if self.consentimiento_at else None
        data["anonimizada"] = self.anonimizada
        return data

    def to_recent_dict(self) -> dict:
        return {
            "id": self.id,
            "departamento": self.departamento,
            "problemas": [p.nombre for p in self._get_problemas()],
            "propuesta": self.propuesta[:200] + "..." if len(self.propuesta) > 200 else self.propuesta,
            "pilar": self.clasificaciones[0].pilar.nombre if self.clasificaciones else None,
            "confianza": self.clasificaciones[0].confianza if self.clasificaciones else None,
            "created_at": self.created_at.isoformat(),
        }

    def _get_problemas(self):
        from app.models.catalog import participacion_problemas, ProblemaCatalogo
        return ProblemaCatalogo.query.join(
            participacion_problemas,
            participacion_problemas.c.problema_id == ProblemaCatalogo.id,
        ).filter(participacion_problemas.c.participacion_id == self.id).all()


class ClasificacionSRIE(db.Model):
    """Resultado del motor de clasificación SRIE para una participación.

    Top-3 clasificaciones con ranking, keywords que dispararon el match, y confianza.
    """

    __tablename__ = "clasificaciones_srie"
    __table_args__ = (
        db.Index("idx_clasif_pilar_confianza", "pilar_id", "confianza"),
        db.Index("idx_clasif_confianza", "confianza"),
        db.Index("idx_clasif_ranking", "participacion_id", "ranking"),
    )

    id = db.Column(db.Integer, primary_key=True)
    participacion_id = db.Column(
        db.Integer, db.ForeignKey("participaciones.id"), nullable=False, index=True
    )
    pilar_id = db.Column(db.Integer, db.ForeignKey("pilares.id"), nullable=False)
    linea_id = db.Column(
        db.Integer, db.ForeignKey("lineas_estrategicas.id"), nullable=True
    )
    componente_id = db.Column(
        db.Integer, db.ForeignKey("componentes.id"), nullable=True
    )
    objetivo_id = db.Column(
        db.Integer, db.ForeignKey("objetivos.id"), nullable=True
    )
    confianza = db.Column(db.Float, nullable=False)  # 0.0 - 1.0
    ranking = db.Column(db.Integer, nullable=False, default=1)  # 1 = principal, 2, 3
    keywords_evidencia = db.Column(db.Text, nullable=True)  # JSON array of matched keywords
    modelo_usado = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    # Relaciones
    pilar = db.relationship("Pilar", lazy="joined")
    linea = db.relationship("LineaEstrategica", lazy="joined")
    componente = db.relationship("Componente", lazy="joined")
    objetivo = db.relationship("Objetivo", lazy="joined")

    def __repr__(self) -> str:
        return f"<ClasificacionSRIE pilar={self.pilar_id} confianza={self.confianza} ranking={self.ranking}>"

    def to_dict(self) -> dict:
        import json
        keywords = []
        if self.keywords_evidencia:
            try:
                keywords = json.loads(self.keywords_evidencia)
            except (json.JSONDecodeError, TypeError):
                keywords = []
        return {
            "id": self.id,
            "pilar": self.pilar.to_dict() if self.pilar else None,
            "linea": self.linea.to_dict() if self.linea else None,
            "componente": self.componente.to_dict() if self.componente else None,
            "objetivo": self.objetivo.to_dict() if self.objetivo else None,
            "confianza": round(self.confianza, 2),
            "ranking": self.ranking,
            "keywords_evidencia": keywords,
            "modelo_usado": self.modelo_usado,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
