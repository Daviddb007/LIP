"""Rutas del módulo de Armonización Estratégica."""
from __future__ import annotations

from flask import Blueprint, jsonify, render_template

from app.services.armonizacion_service import generar_armonizacion

armonizacion_bp = Blueprint("armonizacion", __name__)


@armonizacion_bp.route("/armonizacion")
def pagina():
    return render_template("armonizacion.html")


@armonizacion_bp.route("/api/armonizacion")
def api_armonizacion():
    data = generar_armonizacion()
    return jsonify(data)
