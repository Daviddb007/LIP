"""Rutas de la Biblioteca de Políticas Públicas."""
from __future__ import annotations

from flask import Blueprint, jsonify, render_template, request

from app.models.catalog import Sector
from app.models.politica import Politica
from app.services.srie.keywords import KEYWORDS_PILARES

biblioteca_bp = Blueprint("biblioteca", __name__)


@biblioteca_bp.route("/biblioteca")
def lista():
    sectores = Sector.query.filter_by(activo=True).order_by(Sector.orden).all()
    estado_filter = request.args.get("estado", "")
    sector_filter = request.args.get("sector", "")

    query = Politica.query.filter_by(activo=True)

    if estado_filter:
        query = query.filter(Politica.estado == estado_filter)
    if sector_filter:
        query = query.filter(Politica.sector_id == int(sector_filter))

    politicas = query.order_by(Politica.updated_at.desc()).all()

    return render_template(
        "biblioteca.html",
        politicas=politicas,
        sectores=sectores,
        filtro_estado=estado_filter,
        filtro_sector=sector_filter,
    )


@biblioteca_bp.route("/biblioteca/<int:politica_id>")
def detalle(politica_id: int):
    politica = Politica.query.get(politica_id)
    if not politica or not politica.activo:
        return render_template("404.html"), 404
    return render_template("biblioteca_detalle.html", politica=politica)


@biblioteca_bp.route("/api/politicas")
def api_lista():
    sector_filter = request.args.get("sector", "")
    query = Politica.query.filter_by(activo=True)
    if sector_filter:
        query = query.filter(Politica.sector_id == int(sector_filter))
    politicas = query.order_by(Politica.updated_at.desc()).all()
    return jsonify([p.to_dict() for p in politicas])


@biblioteca_bp.route("/api/politicas/<int:politica_id>")
def api_detalle(politica_id: int):
    politica = Politica.query.get(politica_id)
    if not politica or not politica.activo:
        return jsonify({"error": "Política no encontrada"}), 404
    return jsonify(politica.to_dict())


@biblioteca_bp.route("/api/politicas/<int:politica_id>/preguntar", methods=["POST"])
def api_preguntar(politica_id: int):
    politica = Politica.query.get(politica_id)
    if not politica or not politica.activo:
        return jsonify({"error": "Política no encontrada"}), 404

    data = request.get_json(silent=True) or {}
    pregunta = data.get("pregunta", "").strip()

    if not pregunta:
        return jsonify({"error": "Pregunta requerida"}), 400

    pilar_matches = []
    pregunta_lower = pregunta.lower()
    for pilar_slug, kw_list in KEYWORDS_PILARES.items():
        for keyword, _ in kw_list:
            if keyword.lower() in pregunta_lower:
                pilar_matches.append(pilar_slug)
                break

    return jsonify({
        "politica_id": politica.id,
        "pregunta": pregunta,
        "pilares_relacionados": pilar_matches[:3],
        "respuesta": f"La política '{politica.titulo}' está relacionada con los pilares identificados.",
    })
