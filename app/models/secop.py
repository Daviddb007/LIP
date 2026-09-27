"""Modelos del visor SECOP II (contratación pública de Colombia).

SecopProceso: proceso con oferta abierta descargado del dataset SECOP II
(datos.gov.co, dataset `p6dx-8zbt`), normalizado y validado antes de persistir.
SecopCorte: metadatos de cada descarga (fecha de corte, total de procesos).
LeadSecop: leads del formulario del servicio de licitación (/secop/licitar).
"""
from __future__ import annotations

from datetime import datetime, timezone

from app import db


def _utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class SecopProceso(db.Model):
    """Proceso de contratación pública con oferta abierta."""

    __tablename__ = "secop_procesos"
    __table_args__ = (
        db.UniqueConstraint("url", "corte", name="uq_secop_url_corte"),
        db.Index("idx_secop_departamento", "departamento"),
        db.Index("idx_secop_fecha_limite", "fecha_limite"),
        db.Index("idx_secop_corte", "corte"),
    )

    id = db.Column(db.Integer, primary_key=True)
    entidad = db.Column(db.String(255), nullable=False)
    departamento = db.Column(db.String(100), nullable=False, index=True)
    ciudad = db.Column(db.String(100), nullable=False)
    nombre = db.Column(db.Text, nullable=False)
    modalidad = db.Column(db.String(120), nullable=False)
    tipo_contrato = db.Column(db.String(120), nullable=False, default="No Especificado")
    valor = db.Column(db.BigInteger, nullable=False, default=0)
    requiere_rup = db.Column(db.Boolean, nullable=False, default=True)
    fecha_limite = db.Column(db.Date, nullable=False, index=True)
    corte = db.Column(db.Date, nullable=False, index=True)
    temas = db.Column(db.JSON, nullable=False, default=list)
    pilares = db.Column(db.JSON, nullable=False, default=list)
    url = db.Column(db.String(500), nullable=False)
    creado_at = db.Column(db.DateTime, default=_utcnow, nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "entidad": self.entidad,
            "departamento": self.departamento,
            "ciudad": self.ciudad,
            "nombre": self.nombre,
            "modalidad": self.modalidad,
            "tipo_contrato": self.tipo_contrato,
            "valor": self.valor,
            "requiere_rup": self.requiere_rup,
            "fecha_limite": self.fecha_limite.isoformat(),
            "corte": self.corte.isoformat(),
            "temas": self.temas,
            "pilares": self.pilares,
            "url": self.url,
        }


class SecopCorte(db.Model):
    """Metadatos de una descarga SECOP II."""

    __tablename__ = "secop_cortes"

    id = db.Column(db.Integer, primary_key=True)
    corte = db.Column(db.Date, nullable=False, unique=True)
    generado_at = db.Column(db.DateTime, default=_utcnow, nullable=False)
    total = db.Column(db.Integer, nullable=False, default=0)


class LeadSecop(db.Model):
    """Lead del formulario del servicio de licitación pública."""

    __tablename__ = "secop_leads"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    empresa = db.Column(db.String(160), nullable=False)
    email = db.Column(db.String(160), nullable=False, index=True)
    telefono = db.Column(db.String(40), nullable=False)
    sector = db.Column(db.String(160), nullable=True)
    estado_rup = db.Column(db.String(60), nullable=True)
    mensaje = db.Column(db.Text, nullable=True)
    creado_at = db.Column(db.DateTime, default=_utcnow, nullable=False, index=True)
    atendido = db.Column(db.Boolean, nullable=False, default=False)
