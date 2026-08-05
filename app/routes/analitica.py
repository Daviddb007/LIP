"""Rutas del módulo de Analítica Avanzada."""
from __future__ import annotations

from flask import Blueprint, jsonify, render_template

from app.services.analitica_service import obtener_analitica

analitica_bp = Blueprint("analitica", __name__)


@analitica_bp.route("/analitica")
def pagina():
    return render_template("analitica.html")


@analitica_bp.route("/api/analitica")
def api_analitica():
    data = obtener_analitica()
    return jsonify(data)
