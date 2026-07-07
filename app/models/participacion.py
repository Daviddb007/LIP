from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from app import db

if TYPE_CHECKING:
    from app.models.sector import Sector


participacion_sectores = db.Table(
    'participacion_sectores',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('participacion_id', db.Integer, db.ForeignKey('participaciones.id')),
    db.Column('sector_id', db.Integer, db.ForeignKey('sectores.id')),
)


class Participacion(db.Model):
    __tablename__ = 'participaciones'

    id = db.Column(db.Integer, primary_key=True)
    departamento = db.Column(db.String(100), index=True)
    municipio = db.Column(db.String(100))
    rango_edad = db.Column(db.String(50))
    genero = db.Column(db.String(50))
    sector_prioritario_id = db.Column(db.Integer, db.ForeignKey('sectores.id'), index=True)
    problema_principal = db.Column(db.String(200))
    problema_otro = db.Column(db.Text)
    contexto_ciudadano = db.Column(db.Text)
    actores_responsables = db.Column(db.String(300))
    beneficiarios = db.Column(db.String(300))
    propuesta = db.Column(db.Text, nullable=False)
    srie_pilar = db.Column(db.String(100))
    srie_urgencia = db.Column(db.String(50))
    srie_impacto = db.Column(db.String(50))
    srie_explicacion = db.Column(db.Text)
    ip_hash = db.Column(db.String(64))
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    sectores = db.relationship(
        'Sector',
        secondary=participacion_sectores,
        back_populates='participaciones',
    )
    sector_prioritario = db.relationship(
        'Sector', foreign_keys=[sector_prioritario_id]
    )

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'departamento': self.departamento,
            'municipio': self.municipio,
            'rango_edad': self.rango_edad,
            'genero': self.genero,
            'sector_prioritario_id': self.sector_prioritario_id,
            'problema_principal': self.problema_principal,
            'problema_otro': self.problema_otro,
            'contexto_ciudadano': self.contexto_ciudadano,
            'actores_responsables': self.actores_responsables,
            'beneficiarios': self.beneficiarios,
            'propuesta': self.propuesta,
            'srie_pilar': self.srie_pilar,
            'srie_urgencia': self.srie_urgencia,
            'srie_impacto': self.srie_impacto,
            'srie_explicacion': self.srie_explicacion,
            'ip_hash': self.ip_hash,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'sectores': [s.to_dict() for s in self.sectores],
        }

    def to_admin_dict(self) -> dict:
        return {
            'id': self.id,
            'fecha': self.created_at.strftime('%d/%m/%Y %H:%M') if self.created_at else '',
            'departamento': self.departamento,
            'municipio': self.municipio,
            'rango_edad': self.rango_edad,
            'genero': self.genero,
            'propuesta': self.propuesta,
            'problema_principal': self.problema_principal,
            'contexto_ciudadano': self.contexto_ciudadano,
            'actores_responsables': self.actores_responsables,
            'beneficiarios': self.beneficiarios,
            'srie_pilar': self.srie_pilar,
            'srie_urgencia': self.srie_urgencia,
            'srie_impacto': self.srie_impacto,
            'sectores': [s.nombre for s in self.sectores],
        }

    def to_csv_row(self) -> list:
        return [
            self.id,
            self.created_at.strftime('%d/%m/%Y %H:%M') if self.created_at else '',
            self.departamento,
            self.municipio,
            self.rango_edad,
            self.genero,
            self.sector_prioritario_id,
            self.problema_principal,
            self.contexto_ciudadano,
            self.actores_responsables,
            self.beneficiarios,
            self.propuesta,
            self.srie_pilar,
            self.srie_urgencia,
            self.srie_impacto,
            self.ip_hash,
        ]

    def to_recent_dict(self) -> dict:
        return {
            'propuesta': self.propuesta,
            'departamento': self.departamento,
            'fecha': self.created_at.strftime('%d/%m/%Y') if self.created_at else '',
        }

    @classmethod
    def find_paginated(
        cls,
        *,
        page: int = 1,
        per_page: int = 50,
        departamento=None,
        sector=None,
        rango_edad=None,
        genero=None,
        busqueda=None,
    ):
        from app.models.sector import Sector

        query = cls.query

        if departamento:
            query = query.filter(cls.departamento == departamento)
        if sector:
            query = query.join(cls.sectores).filter(Sector.nombre == sector)
        if rango_edad:
            query = query.filter(cls.rango_edad == rango_edad)
        if genero:
            query = query.filter(cls.genero == genero)
        if busqueda:
            search_term = f'%{busqueda}%'
            query = query.filter(cls.propuesta.ilike(search_term))

        return query.order_by(cls.created_at.desc()).paginate(
            page=page, per_page=per_page
        )

    def __repr__(self) -> str:
        return f'<Participacion {self.id}>'
