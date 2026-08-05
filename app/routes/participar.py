"""Blueprint de participación ciudadana v2.

Formulario 5 pasos + POST /api/enviar + SRIE classification (top-3).
"""
from __future__ import annotations

from datetime import datetime, timezone

from flask import Blueprint, current_app, render_template, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from app import db, limiter, csrf
from app.decorators import get_client_ip, hash_ip
from app.errors import ValidationError, DatabaseError
from app.models.participacion import Participacion
from app.models.catalog import (
    ProblemaCatalogo, Actor, Beneficiario,
    participacion_problemas, participacion_actores, participacion_beneficiarios,
)
from app.services.validation import validate_participacion, validate_consentimiento
from app.services.srie.classifier import clasificar_participacion

participar_bp = Blueprint("participar", __name__)


@participar_bp.route("/participar")
def participar():
    return render_template("participar.html")


@participar_bp.route("/api/catalogo/sectores")
def api_sectores():
    """Retorna sectores con subsectores y problemas anidados."""
    from app.models.catalog import Sector, Subsector

    sectores = Sector.query.filter_by(activo=True).order_by(Sector.orden).all()
    result = []
    for s in sectores:
        sub_data = []
        for sub in s.subsectores:
            if not sub.activo:
                continue
            probs = [
                p.to_dict() for p in sub.problemas if p.activo
            ]
            sub_data.append({**sub.to_dict(), "problemas": probs})
        result.append({**s.to_dict(), "subsectores": sub_data})
    return jsonify(result)


@participar_bp.route("/api/catalogo/actores")
def api_actores():
    from app.models.catalog import Actor
    actores = Actor.query.filter_by(activo=True).order_by(Actor.orden).all()
    return jsonify([a.to_dict() for a in actores])


@participar_bp.route("/api/catalogo/beneficiarios")
def api_beneficiarios():
    from app.models.catalog import Beneficiario
    beneficiarios = Beneficiario.query.filter_by(activo=True).order_by(Beneficiario.orden).all()
    return jsonify([b.to_dict() for b in beneficiarios])


@participar_bp.route("/api/enviar", methods=["POST"])
@csrf.exempt
@limiter.limit(lambda: current_app.config.get("RATELIMIT_ENVIAR", "5 per minute;20 per hour"))
def api_enviar():
    data = request.get_json(silent=True)
    if not data:
        raise ValidationError("Se esperaba JSON")

    # Validar y sanitizar
    consentimiento = validate_consentimiento(data)
    sanitized = validate_participacion(data)

    ip = get_client_ip()
    ip_h = hash_ip(ip)

    participacion = Participacion(
        departamento=sanitized["departamento"],
        municipio=sanitized["municipio"],
        zona=sanitized["zona"],
        justificacion=sanitized["justificacion"],
        propuesta=sanitized["propuesta"],
        rango_edad=sanitized.get("rango_edad"),
        genero=sanitized.get("genero"),
        ip_hash=ip_h,
        consentimiento_aceptado=consentimiento["consentimiento_aceptado"],
        consentimiento_version=consentimiento["consentimiento_version"],
        consentimiento_at=datetime.now(timezone.utc).replace(tzinfo=None),
    )

    try:
        db.session.add(participacion)
        db.session.flush()
    except Exception:
        db.session.rollback()
        raise DatabaseError("Error al guardar la participación")

    # Asociar problemas M:N
    try:
        for pid in sanitized["problema_ids"]:
            db.session.execute(
                participacion_problemas.insert().values(
                    participacion_id=participacion.id, problema_id=int(pid)
                )
            )
    except Exception:
        db.session.rollback()
        raise DatabaseError("Error al asociar problemas")

    # Asociar actores M:N
    try:
        for aid in sanitized.get("actor_ids", []):
            db.session.execute(
                participacion_actores.insert().values(
                    participacion_id=participacion.id, actor_id=int(aid)
                )
            )
    except Exception:
        db.session.rollback()
        raise DatabaseError("Error al asociar actores")

    # Asociar beneficiarios M:N
    try:
        for bid in sanitized.get("beneficiario_ids", []):
            db.session.execute(
                participacion_beneficiarios.insert().values(
                    participacion_id=participacion.id, beneficiario_id=int(bid)
                )
            )
    except Exception:
        db.session.rollback()
        raise DatabaseError("Error al asociar beneficiarios")

    # Clasificar SRIE (top-3)
    try:
        clasificaciones, explicaciones = clasificar_participacion(participacion)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise DatabaseError("Error al clasificar la participación")

    # Retornar top-3
    top_clasif = clasificaciones[0] if clasificaciones else None
    return jsonify({
        "success": True,
        "id": participacion.id,
        "clasificaciones": [
            {
                "pilar": c.pilar.to_dict() if c.pilar else None,
                "confianza": c.confianza,
                "ranking": c.ranking,
                "keywords": c.keywords_evidencia,
                "explicacion": e,
            }
            for c, e in zip(clasificaciones, explicaciones)
        ],
        "clasificacion": {
            "pilar": top_clasif.pilar.to_dict() if top_clasif and top_clasif.pilar else None,
            "confianza": top_clasif.confianza if top_clasif else 0,
            "explicacion": explicaciones[0] if explicaciones else "",
        },
    }), 201
