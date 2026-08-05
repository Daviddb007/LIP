"""Rutas del Asistente Público SRIE (chatbot)."""
from __future__ import annotations

from flask import Blueprint, jsonify, render_template, request

from app.services.asistente_service import responder

asistente_bp = Blueprint("asistente", __name__)


@asistente_bp.route("/asistente")
def pagina():
    return render_template("asistente.html")


@asistente_bp.route("/api/asistente/preguntar", methods=["POST"])
def api_preguntar():
    data = request.get_json(silent=True) or {}
    pregunta = data.get("pregunta", "").strip()

    if not pregunta:
        return jsonify({"error": "La pregunta es requerida"}), 400

    resultado = responder(pregunta)
    return jsonify(resultado)
