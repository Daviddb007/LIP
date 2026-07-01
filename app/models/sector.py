from __future__ import annotations

from typing import TYPE_CHECKING

from app import db

if TYPE_CHECKING:
    from app.models.problema import Problema
    from app.models.participacion import Participacion


class Sector(db.Model):
    __tablename__ = 'sectores'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    icono = db.Column(db.String(50))
    activo = db.Column(db.Boolean, default=True)

    problemas = db.relationship('Problema', backref='sector', lazy='select')
    participaciones = db.relationship(
        'Participacion',
        secondary='participacion_sectores',
        back_populates='sectores',
    )

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'nombre': self.nombre,
            'icono': self.icono,
            'activo': self.activo,
        }

    @classmethod
    def find_active(cls) -> list:
        return cls.query.filter_by(activo=True).all()

    @classmethod
    def find_by_id(cls, sector_id: int):
        return cls.query.get(sector_id)

    def __repr__(self) -> str:
        return f'<Sector {self.nombre}>'
