"""Ruta del Centro de Conocimiento Público (F2)."""
from __future__ import annotations

from flask import Blueprint, render_template

from app.services.conocimiento_service import obtener_contenido

conocimiento_bp = Blueprint("conocimiento", __name__)


@conocimiento_bp.route("/conocer")
def pagina():
    contenido = obtener_contenido()
    return render_template("conocimiento.html", contenido=contenido)
