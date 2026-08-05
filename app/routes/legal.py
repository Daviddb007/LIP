"""Blueprint de páginas legales (cumplimiento normativo colombiano).

Ley 1581 de 2012 (habeas data), Decreto 1377 de 2013,
Ley 1712 de 2014 (transparencia), Ley 1757 de 2015 (participación ciudadana).
"""
from flask import Blueprint, render_template, current_app

legal_bp = Blueprint("legal", __name__, url_prefix="/legal")


@legal_bp.route("/tratamiento-datos")
def tratamiento_datos():
    return render_template(
        "legal/tratamiento_datos.html",
        consent_version=current_app.config.get("CONSENT_VERSION", "2026-01"),
        retention_until=current_app.config.get("DATA_RETENTION_UNTIL", "2030-12-31"),
    )


@legal_bp.route("/transparencia")
def transparencia():
    return render_template("legal/transparencia.html")


@legal_bp.route("/terminos")
def terminos():
    return render_template("legal/terminos.html")


@legal_bp.route("/privacidad")
def privacidad():
    return render_template("legal/privacidad.html")


@legal_bp.route("/derechos-titulares")
def derechos_titulares():
    return render_template("legal/derechos_titulares.html")


@legal_bp.route("/cookies")
def cookies():
    return render_template("legal/cookies.html")
