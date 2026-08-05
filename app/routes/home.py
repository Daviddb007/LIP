"""Blueprint para la página de inicio."""
from __future__ import annotations

from flask import Blueprint, render_template

from app import db, cache
from app.models.participacion import Participacion
from app.models.catalog import ProblemaCatalogo
from app.models.plan import Pilar

home_bp = Blueprint("home", __name__)


@home_bp.route("/")
@cache.cached(timeout=120)
def index():
    total = Participacion.query.count()
    municipios = db.session.query(
        db.func.count(db.distinct(Participacion.municipio))
    ).scalar() or 0
    pilares = Pilar.query.filter_by(activo=True).count()
    problemas = ProblemaCatalogo.query.filter_by(activo=True).count()

    stats = {
        "total": total,
        "municipios": municipios,
        "pilares": pilares,
        "problemas": problemas,
    }
    return render_template("home.html", stats=stats)
