from __future__ import annotations

from datetime import datetime, timezone

from app import db


class Politica(db.Model):
    __tablename__ = 'politicas'

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(300), nullable=False, index=True)
    sector_id = db.Column(db.Integer, db.ForeignKey('sectores.id'), index=True)
    resumen_ejecutivo = db.Column(db.Text, nullable=False)
    problema = db.Column(db.Text)
    objetivos = db.Column(db.Text)
    poblacion_objetivo = db.Column(db.String(300))
    normatividad = db.Column(db.Text)
    cronologia = db.Column(db.Text)
    entidades_responsables = db.Column(db.String(500))
    indicadores = db.Column(db.Text)
    presupuesto = db.Column(db.String(200))
    estado = db.Column(db.String(50), default='Activa')
    documentos = db.Column(db.Text)
    ods_relacionados = db.Column(db.String(200))
    alcance = db.Column(db.String(100))
    activo = db.Column(db.Boolean, default=True)
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    sector = db.relationship('Sector', foreign_keys=[sector_id])

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'titulo': self.titulo,
            'sector_id': self.sector_id,
            'sector_nombre': self.sector.nombre if self.sector else '',
            'resumen_ejecutivo': self.resumen_ejecutivo,
            'problema': self.problema,
            'objetivos': self.objetivos,
            'poblacion_objetivo': self.poblacion_objetivo,
            'normatividad': self.normatividad,
            'cronologia': self.cronologia,
            'entidades_responsables': self.entidades_responsables,
            'indicadores': self.indicadores,
            'presupuesto': self.presupuesto,
            'estado': self.estado,
            'documentos': self.documentos,
            'ods_relacionados': self.ods_relacionados,
            'alcance': self.alcance,
            'activo': self.activo,
        }

    def __repr__(self) -> str:
        return f'<Politica {self.titulo}>'
