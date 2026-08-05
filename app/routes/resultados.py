"""Blueprint de resultados públicos v2.

Dashboard con estadísticas agregadas, tabla de participaciones recientes, y API.
"""
from __future__ import annotations

from flask import Blueprint, render_template, request, jsonify

from app import db, cache
from app.models.participacion import Participacion, ClasificacionSRIE
from app.models.catalog import ProblemaCatalogo, participacion_problemas, Actor, Beneficiario, participacion_actores, participacion_beneficiarios
from app.models.plan import Pilar

resultados_bp = Blueprint("resultados", __name__)


@resultados_bp.route("/resultados")
@cache.cached(timeout=60)
def resultados():
    total = Participacion.query.count()
    municipios = db.session.query(db.func.count(db.distinct(Participacion.municipio))).scalar() or 0
    pilares = db.session.query(db.func.count(db.distinct(ClasificacionSRIE.pilar_id))).scalar() or 0
    problemas = ProblemaCatalogo.query.filter_by(activo=True).count()

    stats = {
        "total": total,
        "municipios": municipios,
        "pilares": pilares,
        "problemas": problemas,
    }
    return render_template("resultados.html", stats=stats)


@resultados_bp.route("/api/estadisticas")
@cache.cached(timeout=60)
def api_estadisticas():
    total = Participacion.query.count()
    departamentos = (
        db.session.query(
            Participacion.departamento,
            db.func.count(Participacion.id),
        )
        .group_by(Participacion.departamento)
        .order_by(db.func.count(Participacion.id).desc())
        .all()
    )

    # Contar problemas por participaciones M:N
    problemas_raw = (
        db.session.query(
            ProblemaCatalogo.nombre,
            db.func.count(participacion_problemas.c.participacion_id),
        )
        .join(
            participacion_problemas,
            participacion_problemas.c.problema_id == ProblemaCatalogo.id,
        )
        .group_by(ProblemaCatalogo.nombre)
        .order_by(db.func.count(participacion_problemas.c.participacion_id).desc())
        .all()
    )

    # Contar actores
    actores_raw = (
        db.session.query(
            Actor.nombre,
            db.func.count(participacion_actores.c.participacion_id),
        )
        .join(
            participacion_actores,
            participacion_actores.c.actor_id == Actor.id,
        )
        .group_by(Actor.nombre)
        .order_by(db.func.count(participacion_actores.c.participacion_id).desc())
        .all()
    )

    # Contar beneficiarios
    beneficiarios_raw = (
        db.session.query(
            Beneficiario.nombre,
            db.func.count(participacion_beneficiarios.c.participacion_id),
        )
        .join(
            participacion_beneficiarios,
            participacion_beneficiarios.c.beneficiario_id == Beneficiario.id,
        )
        .group_by(Beneficiario.nombre)
        .order_by(db.func.count(participacion_beneficiarios.c.participacion_id).desc())
        .all()
    )

    pilares = (
        db.session.query(
            Pilar.nombre,
            db.func.count(ClasificacionSRIE.id),
        )
        .join(Pilar, Pilar.id == ClasificacionSRIE.pilar_id)
        .group_by(Pilar.nombre)
        .order_by(db.func.count(ClasificacionSRIE.id).desc())
        .all()
    )

    return jsonify({
        "total": total,
        "departamentos": [{"nombre": d, "total": c} for d, c in departamentos],
        "problemas": [{"nombre": p, "total": c} for p, c in problemas_raw],
        "actores": [{"nombre": a, "total": c} for a, c in actores_raw],
        "beneficiarios": [{"nombre": b, "total": c} for b, c in beneficiarios_raw],
        "pilares": [{"nombre": p, "total": c} for p, c in pilares],
    })


@resultados_bp.route("/api/participaciones")
@cache.cached(timeout=30, query_string=True)
def api_participaciones():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    pagination = (
        Participacion.query
        .order_by(Participacion.created_at.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )
    return jsonify({
        "participaciones": [p.to_recent_dict() for p in pagination.items],
        "total": pagination.total,
        "pages": pagination.pages,
        "current_page": page,
    })
