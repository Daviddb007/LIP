"""Rutas del módulo SaaS multi-tenant."""
from __future__ import annotations

from flask import Blueprint, jsonify, render_template, request

from app import db
from app.models.organizacion import Organizacion
from app.decorators import login_required

saas_bp = Blueprint("saas", __name__)


@saas_bp.route("/saas")
def landing():
    total_orgs = Organizacion.query.count()
    return render_template("saas.html", total_organizaciones=total_orgs)


@saas_bp.route("/saas/registro")
def registro():
    return render_template("saas_registro.html")


@saas_bp.route("/saas/<slug>")
def org_landing(slug):
    org = Organizacion.por_slug(slug)
    if not org:
        return render_template("saas_org_no_encontrada.html", slug=slug), 404
    return render_template("saas_org.html", org=org)


@saas_bp.route("/api/organizaciones", methods=["GET"])
@login_required
def api_listar():
    orgs = Organizacion.query.order_by(Organizacion.created_at.desc()).all()
    return jsonify([o.to_dict() for o in orgs])


@saas_bp.route("/api/organizaciones", methods=["POST"])
def api_crear():
    data = request.get_json(silent=True) or {}
    nombre = data.get("nombre", "").strip()
    tipo = data.get("tipo", "empresa")

    if not nombre:
        return jsonify({"error": "Nombre requerido"}), 400

    org = Organizacion(
        nombre=nombre,
        slug=Organizacion.generar_slug(nombre),
        tipo=tipo,
        plan=data.get("plan", "gratuito"),
        email_contacto=data.get("email_contacto") or None,
        color=data.get("color") or None,
    )
    db.session.add(org)
    db.session.commit()

    return jsonify(org.to_dict()), 201
