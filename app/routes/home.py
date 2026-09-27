"""Blueprint para la página de inicio."""
from __future__ import annotations

from flask import Blueprint, render_template

from app import db, cache
from app.models.participacion import Participacion
from app.models.catalog import ProblemaCatalogo
from app.models.plan import Pilar
from app.models.secop import SecopCorte

home_bp = Blueprint("home", __name__)


def _stats() -> dict:
    total = Participacion.query.count()
    municipios = db.session.query(
        db.func.count(db.distinct(Participacion.municipio))
    ).scalar() or 0
    pilares = Pilar.query.filter_by(activo=True).count()
    problemas = ProblemaCatalogo.query.filter_by(activo=True).count()
    ultimo_corte = SecopCorte.query.order_by(SecopCorte.corte.desc()).first()
    secop_total = ultimo_corte.total if ultimo_corte else 0
    secop_corte = ultimo_corte.corte.strftime("%d/%m/%Y") if ultimo_corte else "sin datos"
    return {
        "total": total,
        "municipios": municipios,
        "pilares": pilares,
        "problemas": problemas,
        "secop_total": secop_total,
        "secop_corte": secop_corte,
    }


@home_bp.route("/")
@cache.cached(timeout=120)
def index():
    return render_template("home.html", stats=_stats())


@home_bp.route("/presentacion")
@cache.cached(timeout=120)
def presentacion():
    return render_template("presentacion.html", stats=_stats())
