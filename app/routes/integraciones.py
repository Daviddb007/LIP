"""Rutas del Ecosistema de Integraciones."""
from __future__ import annotations

from flask import Blueprint, jsonify, render_template, request

from app import db
from app.models.webhook import Webhook
from app.decorators import login_required
from app.services.integracion_service import PARTNERS

integraciones_bp = Blueprint("integraciones", __name__)


@integraciones_bp.route("/ecosistema")
def pagina():
    webhooks = Webhook.query.order_by(Webhook.created_at.desc()).all()
    return render_template(
        "integraciones.html",
        partners=PARTNERS,
        webhooks=webhooks,
    )


@integraciones_bp.route("/api/webhooks", methods=["GET"])
@login_required
def api_webhooks_listar():
    webhooks = Webhook.query.order_by(Webhook.created_at.desc()).all()
    return jsonify([w.to_dict() for w in webhooks])


@integraciones_bp.route("/api/webhooks", methods=["POST"])
@login_required
def api_webhooks_crear():
    data = request.get_json(silent=True) or {}
    nombre = data.get("nombre", "").strip()
    url = data.get("url", "").strip()
    evento = data.get("evento", "").strip()

    if not nombre or not url or not evento:
        return jsonify({"error": "nombre, url y evento son requeridos"}), 400

    wh = Webhook(nombre=nombre, url=url, evento=evento, activo=True)
    db.session.add(wh)
    db.session.commit()

    return jsonify(wh.to_dict()), 201


@integraciones_bp.route("/api/webhooks/<int:wh_id>", methods=["DELETE"])
@login_required
def api_webhooks_eliminar(wh_id: int):
    wh = Webhook.query.get(wh_id)
    if not wh:
        return jsonify({"error": "Webhook no encontrado"}), 404

    db.session.delete(wh)
    db.session.commit()

    return jsonify({"mensaje": "Webhook eliminado"})
