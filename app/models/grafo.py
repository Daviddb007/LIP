"""
Modelos de la "Estrategia de participación robusta" — Pipeline de conocimiento.

Grupo Focal B:
    TranscriptFocal    → Texto plano completo de una sesión (whisper local).
    SegmentoTranscript → Segmentos con timestamps del transcript.
    NodoGrafo          → Chunk/nodo del grafo de conocimiento.
    RelacionGrafo      → Arista entre nodos (secuencia / similitud / tema).

Referencias cruzadas con app/models/focal.py (SesionFocal, AudioFocal).
"""
from __future__ import annotations

from datetime import datetime, timezone

from app import db


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class TranscriptFocal(db.Model):
    """Transcripción completa de una sesión de grupo focal."""

    __tablename__ = "transcripts_focales"
    __table_args__ = (
        db.Index("idx_transcript_sesion", "sesion_id"),
    )

    id = db.Column(db.Integer, primary_key=True)
    sesion_id = db.Column(db.Integer, db.ForeignKey("sesiones_focales.id"), nullable=False)
    texto_completo = db.Column(db.Text, nullable=False)
    formato = db.Column(db.String(10), nullable=False, default="txt")
    modelo_usado = db.Column(db.String(100), nullable=True)
    idioma = db.Column(db.String(10), nullable=True)
    duracion_segundos = db.Column(db.Float, nullable=True)
    procesado_por = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=_now, nullable=False)
    updated_at = db.Column(db.DateTime, default=_now, onupdate=_now, nullable=False)

    segmentos = db.relationship(
        "SegmentoTranscript", backref="transcript",
        cascade="all, delete-orphan", lazy="select",
        order_by="SegmentoTranscript.inicio_seg",
    )
    nodos = db.relationship(
        "NodoGrafo", backref="transcript",
        cascade="all, delete-orphan", lazy="select",
    )

    def __repr__(self) -> str:
        return f"<TranscriptFocal sesion={self.sesion_id}>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "sesion_id": self.sesion_id,
            "palabras": len(self.texto_completo.split()),
            "formato": self.formato,
            "modelo_usado": self.modelo_usado,
            "idioma": self.idioma,
            "duracion_segundos": self.duracion_segundos,
            "total_segmentos": len(self.segmentos),
            "total_nodos": len(self.nodos),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class SegmentoTranscript(db.Model):
    """Segmento con timestamp de una transcripción."""

    __tablename__ = "segmentos_transcript"
    __table_args__ = (
        db.Index("idx_segmento_transcript", "transcript_id"),
    )

    id = db.Column(db.Integer, primary_key=True)
    transcript_id = db.Column(db.Integer, db.ForeignKey("transcripts_focales.id"), nullable=False)
    audio_id = db.Column(db.Integer, db.ForeignKey("audios_focales.id", ondelete="SET NULL"), nullable=True)
    inicio_seg = db.Column(db.Float, nullable=False, default=0)
    fin_seg = db.Column(db.Float, nullable=False, default=0)
    texto = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=_now, nullable=False)

    def __repr__(self) -> str:
        return f"<Segmento {self.inicio_seg:.1f}-{self.fin_seg:.1f}s>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "transcript_id": self.transcript_id,
            "audio_id": self.audio_id,
            "inicio_seg": self.inicio_seg,
            "fin_seg": self.fin_seg,
            "texto": self.texto,
        }


class NodoGrafo(db.Model):
    """Nodo del grafo de conocimiento derivado de una sesión."""

    __tablename__ = "nodos_grafo"
    __table_args__ = (
        db.Index("idx_nodo_transcript", "transcript_id"),
        db.Index("idx_nodo_sesion", "sesion_id"),
        db.Index("idx_nodo_tipo", "tipo"),
    )

    id = db.Column(db.Integer, primary_key=True)
    transcript_id = db.Column(db.Integer, db.ForeignKey("transcripts_focales.id", ondelete="CASCADE"), nullable=False)
    sesion_id = db.Column(db.Integer, db.ForeignKey("sesiones_focales.id", ondelete="CASCADE"), nullable=False)
    tipo = db.Column(db.String(30), nullable=False, default="segmento")
    titulo = db.Column(db.String(300), nullable=True)
    texto = db.Column(db.Text, nullable=False)
    sector_id = db.Column(db.Integer, db.ForeignKey("catalogo_sectores.id"), nullable=True)
    tema = db.Column(db.String(200), nullable=True)
    keywords = db.Column(db.Text, nullable=True)       # JSON array de keywords
    embedding = db.Column(db.Text, nullable=True)      # JSON array (vector) — opcional
    metadatos = db.Column(db.Text, nullable=True)      # JSON dict (inicio/fin, fuente, etc.)
    origen = db.Column(db.String(30), nullable=False, default="transcript")
    created_at = db.Column(db.DateTime, default=_now, nullable=False)

    sector = db.relationship("Sector", foreign_keys=[sector_id], lazy="joined")

    TIPOS = [
        ("segmento", "Segmento"),
        ("tema", "Tema"),
        ("problema", "Problemática"),
    ]

    def __repr__(self) -> str:
        return f"<NodoGrafo {self.tipo}: {self.titulo or self.texto[:50]}>"

    def to_dict(self) -> dict:
        import json

        def _load(value):
            if not value:
                return None
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return None

        return {
            "id": self.id,
            "transcript_id": self.transcript_id,
            "sesion_id": self.sesion_id,
            "tipo": self.tipo,
            "titulo": self.titulo,
            "texto": self.texto,
            "sector_id": self.sector_id,
            "sector_nombre": self.sector.nombre if self.sector else "",
            "tema": self.tema,
            "keywords": _load(self.keywords) or [],
            "metadatos": _load(self.metadatos) or {},
            "origen": self.origen,
        }


class RelacionGrafo(db.Model):
    """Arista entre nodos del grafo de conocimiento."""

    __tablename__ = "relaciones_grafo"
    __table_args__ = (
        db.Index("idx_relacion_origen", "nodo_origen_id"),
        db.Index("idx_relacion_destino", "nodo_destino_id"),
        db.UniqueConstraint("nodo_origen_id", "nodo_destino_id", "tipo", name="uq_relacion_grafo"),
    )

    id = db.Column(db.Integer, primary_key=True)
    nodo_origen_id = db.Column(db.Integer, db.ForeignKey("nodos_grafo.id", ondelete="CASCADE"), nullable=False)
    nodo_destino_id = db.Column(db.Integer, db.ForeignKey("nodos_grafo.id", ondelete="CASCADE"), nullable=False)
    tipo = db.Column(db.String(30), nullable=False, default="similitud")
    peso = db.Column(db.Float, nullable=False, default=0.0)
    created_at = db.Column(db.DateTime, default=_now, nullable=False)

    origen = db.relationship("NodoGrafo", foreign_keys=[nodo_origen_id], lazy="joined")
    destino = db.relationship("NodoGrafo", foreign_keys=[nodo_destino_id], lazy="joined")

    TIPOS = [
        ("secuencia", "Secuencia"),
        ("similitud", "Similitud semántica"),
        ("tema", "Tema compartido"),
    ]

    def __repr__(self) -> str:
        return f"<Relacion {self.tipo} {self.nodo_origen_id}→{self.nodo_destino_id} {self.peso:.2f}>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "origen": self.nodo_origen_id,
            "destino": self.nodo_destino_id,
            "tipo": self.tipo,
            "peso": round(self.peso, 3),
        }
