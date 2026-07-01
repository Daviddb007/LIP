from __future__ import annotations

from app import db


class Problema(db.Model):
    __tablename__ = 'catalogo_problemas'

    id = db.Column(db.Integer, primary_key=True)
    sector_id = db.Column(db.Integer, db.ForeignKey('sectores.id'), nullable=False)
    nombre = db.Column(db.String(200), nullable=False)
    activo = db.Column(db.Boolean, default=True)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'sector_id': self.sector_id,
            'nombre': self.nombre,
            'activo': self.activo,
        }

    @classmethod
    def find_active_by_sector(cls, sector_id: int) -> list:
        return cls.query.filter_by(sector_id=sector_id, activo=True).all()

    def __repr__(self) -> str:
        return f'<Problema {self.nombre}>'
