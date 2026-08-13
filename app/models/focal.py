"""
Modelos de la "Estrategia de participación robusta" — Grupos Focales.

Grupo Focal A:
    OrgFocal           → Organización interesada en ser representada.
    SesionFocal        → Sesión de grupo focal.
    ParticipanteFocal  → Participante + consentimiento Ley 1581.
    PreguntaFocal      → Preguntas guía por sesión (incluye las de valor percibido del presupuesto).
    AudioFocal         → Grabación de la sesión (almacenamiento reservado, fuera del web root).

Pipeline B (transcripción → grafo) vive en app/models/grafo.py.
"""
from __future__ import annotations

from datetime import datetime, timezone

from app import db


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class OrgFocal(db.Model):
    """Organización interesada en ser representada en un grupo focal."""

    __tablename__ = "orgs_focales"
    __table_args__ = (
        db.Index("idx_orgfocal_sector", "sector_id"),
        db.Index("idx_orgfocal_activo", "activo"),
    )

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False, unique=True)
    tipo = db.Column(db.String(50), nullable=False, default="gremio")
    sector_id = db.Column(db.Integer, db.ForeignKey("catalogo_sectores.id"), nullable=True)
    descripcion = db.Column(db.Text, nullable=True)
    contacto_nombre = db.Column(db.String(150), nullable=True)
    contacto_email = db.Column(db.String(200), nullable=True)
    contacto_telefono = db.Column(db.String(50), nullable=True)
    activo = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=_now, nullable=False)
    updated_at = db.Column(db.DateTime, default=_now, onupdate=_now, nullable=False)

    sector = db.relationship("Sector", foreign_keys=[sector_id], lazy="joined")
    sesiones = db.relationship(
        "SesionFocal", backref="organizacion",
        cascade="all, delete-orphan", lazy="select",
        order_by="SesionFocal.fecha.desc()",
    )

    TIPOS = [
        ("gremio", "Gremio"),
        ("universidad", "Universidad"),
        ("ong", "ONG"),
        ("centro_pensamiento", "Centro de Pensamiento"),
        ("empresa", "Empresa"),
        ("cooperacion", "Cooperación Internacional"),
        ("comunidad", "Comunidad / Sociedad civil"),
        ("otra", "Otra"),
    ]

    def __repr__(self) -> str:
        return f"<OrgFocal {self.nombre}>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "tipo": self.tipo,
            "tipo_label": dict(self.TIPOS).get(self.tipo, self.tipo),
            "sector_id": self.sector_id,
            "sector_nombre": self.sector.nombre if self.sector else "",
            "descripcion": self.descripcion,
            "contacto_nombre": self.contacto_nombre,
            "contacto_email": self.contacto_email,
            "contacto_telefono": self.contacto_telefono,
            "activo": self.activo,
            "total_sesiones": len(self.sesiones),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class SesionFocal(db.Model):
    """Sesión de grupo focal con una organización."""

    __tablename__ = "sesiones_focales"
    __table_args__ = (
        db.Index("idx_sesion_org", "org_id"),
        db.Index("idx_sesion_estado", "estado"),
        db.Index("idx_sesion_fecha", "fecha"),
    )

    id = db.Column(db.Integer, primary_key=True)
    org_id = db.Column(db.Integer, db.ForeignKey("orgs_focales.id"), nullable=False)
    titulo = db.Column(db.String(250), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    modalidad = db.Column(db.String(30), nullable=False, default="presencial")
    lugar = db.Column(db.String(250), nullable=True)
    objetivo = db.Column(db.Text, nullable=True)
    estado = db.Column(db.String(30), nullable=False, default="programada")
    created_at = db.Column(db.DateTime, default=_now, nullable=False)
    updated_at = db.Column(db.DateTime, default=_now, onupdate=_now, nullable=False)

    participantes = db.relationship(
        "ParticipanteFocal", backref="sesion",
        cascade="all, delete-orphan", lazy="select",
    )
    preguntas = db.relationship(
        "PreguntaFocal", backref="sesion",
        cascade="all, delete-orphan", lazy="select",
        order_by="PreguntaFocal.orden",
    )
    audios = db.relationship(
        "AudioFocal", backref="sesion",
        cascade="all, delete-orphan", lazy="select",
    )
    transcript = db.relationship(
        "TranscriptFocal", backref="sesion",
        cascade="all, delete-orphan", lazy="select",
        uselist=False,
    )

    MODALIDADES = [("presencial", "Presencial"), ("virtual", "Virtual"), ("hibrida", "Híbrida")]
    ESTADOS = [("programada", "Programada"), ("en_curso", "En curso"), ("finalizada", "Finalizada")]

    def __repr__(self) -> str:
        return f"<SesionFocal {self.titulo}>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "org_id": self.org_id,
            "org_nombre": self.organizacion.nombre if self.organizacion else "",
            "titulo": self.titulo,
            "fecha": self.fecha.isoformat() if self.fecha else None,
            "modalidad": self.modalidad,
            "lugar": self.lugar,
            "objetivo": self.objetivo,
            "estado": self.estado,
            "total_participantes": len(self.participantes),
            "total_preguntas": len(self.preguntas),
            "total_audios": len(self.audios),
            "tiene_transcript": self.transcript is not None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ParticipanteFocal(db.Model):
    """Participante de una sesión de grupo focal con consentimiento Ley 1581."""

    __tablename__ = "participantes_focales"
    __table_args__ = (
        db.Index("idx_partfocal_sesion", "sesion_id"),
    )

    id = db.Column(db.Integer, primary_key=True)
    sesion_id = db.Column(db.Integer, db.ForeignKey("sesiones_focales.id"), nullable=False)
    nombre = db.Column(db.String(200), nullable=False)
    cargo = db.Column(db.String(200), nullable=True)
    email = db.Column(db.String(200), nullable=True)
    telefono = db.Column(db.String(50), nullable=True)

    # Consentimiento (Ley 1581 de 2012)
    consentimiento_aceptado = db.Column(db.Boolean, nullable=False, default=False)
    consentimiento_version = db.Column(db.String(20), nullable=False, default="2026-01")
    consentimiento_at = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=_now, nullable=False)

    def __repr__(self) -> str:
        return f"<ParticipanteFocal {self.nombre}>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "sesion_id": self.sesion_id,
            "nombre": self.nombre,
            "cargo": self.cargo,
            "email": self.email,
            "telefono": self.telefono,
            "consentimiento_aceptado": self.consentimiento_aceptado,
            "consentimiento_version": self.consentimiento_version,
            "consentimiento_at": self.consentimiento_at.isoformat() if self.consentimiento_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class PreguntaFocal(db.Model):
    """Pregunta guía de una sesión (incluye las de valor percibido del presupuesto)."""

    __tablename__ = "preguntas_focales"
    __table_args__ = (
        db.Index("idx_pregfocal_sesion", "sesion_id"),
    )

    id = db.Column(db.Integer, primary_key=True)
    sesion_id = db.Column(db.Integer, db.ForeignKey("sesiones_focales.id"), nullable=False)
    categoria = db.Column(db.String(30), nullable=False, default="problema")
    texto = db.Column(db.Text, nullable=False)
    orden = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=_now, nullable=False)

    CATEGORIAS = [
        ("problema", "Problemática principal"),
        ("politica", "Política pública"),
        ("presupuesto", "Valor percibido del presupuesto"),
        ("valor_agregado", "Valor agregado para el sector"),
        ("otra", "Otra"),
    ]

    def __repr__(self) -> str:
        return f"<PreguntaFocal {self.texto[:50]}>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "sesion_id": self.sesion_id,
            "categoria": self.categoria,
            "categoria_label": dict(self.CATEGORIAS).get(self.categoria, self.categoria),
            "texto": self.texto,
            "orden": self.orden,
        }


class AudioFocal(db.Model):
    """Grabación de una sesión. Almacenamiento reservado fuera del web root."""

    __tablename__ = "audios_focales"
    __table_args__ = (
        db.Index("idx_audio_sesion", "sesion_id"),
        db.Index("idx_audio_estado", "estado"),
    )

    id = db.Column(db.Integer, primary_key=True)
    sesion_id = db.Column(db.Integer, db.ForeignKey("sesiones_focales.id"), nullable=False)
    nombre_original = db.Column(db.String(250), nullable=False)
    ruta_archivo = db.Column(db.String(500), nullable=False)
    duracion_segundos = db.Column(db.Float, nullable=True)
    tamano_bytes = db.Column(db.Integer, nullable=False)
    formato = db.Column(db.String(10), nullable=False)
    sha256 = db.Column(db.String(64), nullable=False)
    estado = db.Column(db.String(30), nullable=False, default="pendiente")
    error_mensaje = db.Column(db.Text, nullable=True)
    transcript_id = db.Column(db.Integer, db.ForeignKey("transcripts_focales.id", ondelete="SET NULL"), nullable=True)
    creado_por = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=_now, nullable=False)
    updated_at = db.Column(db.DateTime, default=_now, onupdate=_now, nullable=False)

    transcript = db.relationship("TranscriptFocal", foreign_keys=[transcript_id], lazy="joined")

    ESTADOS = [
        ("pendiente", "Pendiente"),
        ("en_cola", "En cola"),
        ("procesando", "Procesando"),
        ("transcrito", "Transcrito"),
        ("error", "Error"),
    ]

    def __repr__(self) -> str:
        return f"<AudioFocal {self.nombre_original}>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "sesion_id": self.sesion_id,
            "nombre_original": self.nombre_original,
            "duracion_segundos": self.duracion_segundos,
            "tamano_bytes": self.tamano_bytes,
            "formato": self.formato,
            "sha256": self.sha256,
            "estado": self.estado,
            "estado_label": dict(self.ESTADOS).get(self.estado, self.estado),
            "error_mensaje": self.error_mensaje,
            "transcript_id": self.transcript_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
