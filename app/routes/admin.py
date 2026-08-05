"""Blueprint del panel administrativo (Centro de Inteligencia) v2.

Módulos: Dashboard, Participaciones, Pilares, Problemas, Clasificaciones,
Planes, Sectores (CRUD), Actores, Beneficiarios, Export, Config, Logs.
"""
from __future__ import annotations

import csv
import io
import json
from datetime import datetime, timedelta, timezone

from werkzeug.security import check_password_hash

from flask import (
    Blueprint, render_template, request, session, redirect,
    url_for, flash, jsonify, Response, current_app,
)

from app import db, cache, limiter
from app.decorators import login_required
from app.models.participacion import Participacion, ClasificacionSRIE
from app.models.plan import Plan, Pilar, LineaEstrategica, Componente, Objetivo
from app.models.catalog import (
    Sector, Subsector, ProblemaCatalogo, Actor, Beneficiario,
    participacion_problemas, participacion_actores, participacion_beneficiarios,
)

admin_bp = Blueprint("admin", __name__)


# ------------------------------------------------------------------
# Auth
# ------------------------------------------------------------------
@admin_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("20 per minute;200 per hour")
def login():
    if session.get("admin"):
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        valid_user = current_app.config.get("ADMIN_USER", "admin")
        valid_pass = current_app.config.get("ADMIN_PASS", "admin")

        if username == valid_user and check_password_hash(valid_pass, password):
            session.permanent = True
            session["admin"] = True
            session["admin_user"] = username
            session["admin_login"] = datetime.now(timezone.utc).isoformat()
            return redirect(url_for("admin.dashboard"))
        flash("Credenciales incorrectas", "error")

    return render_template("admin/login.html")


@admin_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home.index"))


# ------------------------------------------------------------------
# Dashboard principal
# ------------------------------------------------------------------
@admin_bp.route("/")
@login_required
def dashboard():
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    total = Participacion.query.count()
    this_month = Participacion.query.filter(Participacion.created_at >= month_start).count()
    municipios = db.session.query(db.func.count(db.distinct(Participacion.municipio))).scalar() or 0
    pilares_cubiertos = db.session.query(db.func.count(db.distinct(ClasificacionSRIE.pilar_id))).scalar() or 0
    total_pilares = Pilar.query.filter_by(activo=True).count()
    raw_avg = db.session.query(db.func.avg(ClasificacionSRIE.confianza)).scalar() or 0
    avg_conf = round(float(raw_avg) * 100, 1)

    # Top problemas
    top_problemas = (
        db.session.query(
            ProblemaCatalogo.nombre,
            db.func.count(participacion_problemas.c.participacion_id).label("total"),
        )
        .join(
            participacion_problemas,
            participacion_problemas.c.problema_id == ProblemaCatalogo.id,
        )
        .group_by(ProblemaCatalogo.nombre)
        .order_by(db.desc("total"))
        .limit(5)
        .all()
    )

    # Top actores
    top_actores = (
        db.session.query(
            Actor.nombre,
            db.func.count(participacion_actores.c.participacion_id).label("total"),
        )
        .join(
            participacion_actores,
            participacion_actores.c.actor_id == Actor.id,
        )
        .group_by(Actor.nombre)
        .order_by(db.desc("total"))
        .limit(5)
        .all()
    )

    stats = {
        "total": total,
        "this_month": this_month,
        "municipios": municipios,
        "pilares": pilares_cubiertos,
        "total_pilares": total_pilares,
        "coverage": round(pilares_cubiertos / total_pilares * 100) if total_pilares > 0 else 0,
        "avg_confidence": avg_conf,
        "top_problemas": [{"nombre": p, "total": c} for p, c in top_problemas],
        "top_actores": [{"nombre": a, "total": c} for a, c in top_actores],
    }

    participaciones = (
        Participacion.query
        .options(
            db.joinedload(Participacion.clasificaciones).joinedload(ClasificacionSRIE.pilar),
        )
        .order_by(Participacion.created_at.desc())
        .limit(15)
        .all()
    )
    return render_template("admin/dashboard.html", stats=stats, participaciones=participaciones)


# ------------------------------------------------------------------
# Participaciones
# ------------------------------------------------------------------
@admin_bp.route("/participaciones")
@login_required
def participaciones():
    page = request.args.get("page", 1, type=int)
    search = request.args.get("q", "").strip()
    dept = request.args.get("dept", "").strip()
    query = Participacion.query

    if search:
        query = query.filter(
            db.or_(
                Participacion.municipio.ilike(f"%{search}%"),
                Participacion.justificacion.ilike(f"%{search}%"),
                Participacion.propuesta.ilike(f"%{search}%"),
            )
        )
    if dept:
        query = query.filter(Participacion.departamento == dept)

    pagination = (
        query
        .options(
            db.joinedload(Participacion.clasificaciones).joinedload(ClasificacionSRIE.pilar),
        )
        .order_by(Participacion.created_at.desc())
        .paginate(page=page, per_page=20, error_out=False)
    )
    departamentos = db.session.query(db.distinct(Participacion.departamento)).order_by(Participacion.departamento).all()

    return render_template(
        "admin/participaciones.html",
        participaciones=pagination.items,
        pagination=pagination,
        search=search,
        dept=dept,
        departamentos=[d[0] for d in departamentos],
    )


@admin_bp.route("/participaciones/<int:id>")
@login_required
def participacion_detail(id):
    p = Participacion.query.get_or_404(id)
    # Eager load M:N relationships
    problemas = ProblemaCatalogo.query.join(
        participacion_problemas,
        participacion_problemas.c.problema_id == ProblemaCatalogo.id,
    ).filter(participacion_problemas.c.participacion_id == p.id).all()

    actores = Actor.query.join(
        participacion_actores,
        participacion_actores.c.actor_id == Actor.id,
    ).filter(participacion_actores.c.participacion_id == p.id).all()

    beneficiarios = Beneficiario.query.join(
        participacion_beneficiarios,
        participacion_beneficiarios.c.beneficiario_id == Beneficiario.id,
    ).filter(participacion_beneficiarios.c.participacion_id == p.id).all()

    return render_template(
        "admin/participacion_detail.html",
        p=p, problemas=problemas, actores=actores, beneficiarios=beneficiarios,
    )


@admin_bp.route("/participaciones/<int:id>/delete", methods=["POST"])
@login_required
def participacion_delete(id):
    p = Participacion.query.get_or_404(id)
    db.session.delete(p)
    db.session.commit()
    flash(f"Participación #{id} eliminada", "success")
    return redirect(url_for("admin.participaciones"))


# ------------------------------------------------------------------
# Sectores (CRUD)
# ------------------------------------------------------------------
@admin_bp.route("/sectores")
@login_required
def sectores():
    sectores = Sector.query.order_by(Sector.orden).all()
    return render_template("admin/sectores.html", sectores=sectores)


@admin_bp.route("/sectores/<int:id>/toggle", methods=["POST"])
@login_required
def sector_toggle(id):
    s = Sector.query.get_or_404(id)
    s.activo = not s.activo
    db.session.commit()
    flash(f"Sector '{s.nombre}' {'activado' if s.activo else 'desactivado'}", "success")
    return redirect(url_for("admin.sectores"))


@admin_bp.route("/sectores/<int:id>")
@login_required
def sector_detail(id):
    s = Sector.query.get_or_404(id)
    subsectores = Subsector.query.filter_by(sector_id=id).order_by(Subsector.orden).all()
    return render_template("admin/sector_detail.html", sector=s, subsectores=subsectores)


# ------------------------------------------------------------------
# Actores
# ------------------------------------------------------------------
@admin_bp.route("/actores")
@login_required
def actores():
    actores = Actor.query.order_by(Actor.orden).all()
    return render_template("admin/actores.html", actores=actores)


@admin_bp.route("/actores/<int:id>/toggle", methods=["POST"])
@login_required
def actor_toggle(id):
    a = Actor.query.get_or_404(id)
    a.activo = not a.activo
    db.session.commit()
    flash(f"Actor '{a.nombre}' {'activado' if a.activo else 'desactivado'}", "success")
    return redirect(url_for("admin.actores"))


# ------------------------------------------------------------------
# Beneficiarios
# ------------------------------------------------------------------
@admin_bp.route("/beneficiarios")
@login_required
def beneficiarios():
    beneficiarios = Beneficiario.query.order_by(Beneficiario.orden).all()
    return render_template("admin/beneficiarios.html", beneficiarios=beneficiarios)


@admin_bp.route("/beneficiarios/<int:id>/toggle", methods=["POST"])
@login_required
def beneficiario_toggle(id):
    b = Beneficiario.query.get_or_404(id)
    b.activo = not b.activo
    db.session.commit()
    flash(f"Beneficiario '{b.nombre}' {'activado' if b.activo else 'desactivado'}", "success")
    return redirect(url_for("admin.beneficiarios"))


# ------------------------------------------------------------------
# Pilares
# ------------------------------------------------------------------
@admin_bp.route("/pilares")
@login_required
def pilares():
    pilares = Pilar.query.order_by(Pilar.orden).all()
    return render_template("admin/pilares.html", pilares=pilares)


@admin_bp.route("/pilares/<int:id>")
@login_required
def pilar_detail(id):
    pilar = Pilar.query.get_or_404(id)
    lineas = LineaEstrategica.query.filter_by(pilar_id=id).order_by(LineaEstrategica.orden).all()
    count = db.session.query(db.func.count(ClasificacionSRIE.id)).filter(ClasificacionSRIE.pilar_id == id).scalar() or 0
    return render_template("admin/pilar_detail.html", pilar=pilar, lineas=lineas, count=count)


@admin_bp.route("/pilares/<int:id>/toggle", methods=["POST"])
@login_required
def pilar_toggle(id):
    pilar = Pilar.query.get_or_404(id)
    pilar.activo = not pilar.activo
    db.session.commit()
    flash(f"Pilar '{pilar.nombre}' {'activado' if pilar.activo else 'desactivado'}", "success")
    return redirect(url_for("admin.pilares"))


# ------------------------------------------------------------------
# Problemas (catálogo)
# ------------------------------------------------------------------
@admin_bp.route("/problemas")
@login_required
def problemas():
    problemas = ProblemaCatalogo.query.order_by(ProblemaCatalogo.orden).all()
    return render_template("admin/problemas.html", problemas=problemas)


@admin_bp.route("/problemas/<int:id>/toggle", methods=["POST"])
@login_required
def problema_toggle(id):
    p = ProblemaCatalogo.query.get_or_404(id)
    p.activo = not p.activo
    db.session.commit()
    flash(f"Problema '{p.nombre}' {'activado' if p.activo else 'desactivado'}", "success")
    return redirect(url_for("admin.problemas"))


# ------------------------------------------------------------------
# Clasificaciones
# ------------------------------------------------------------------
@admin_bp.route("/clasificaciones")
@login_required
def clasificaciones():
    page = request.args.get("page", 1, type=int)
    nivel = request.args.get("nivel", "").strip()

    query = ClasificacionSRIE.query
    if nivel == "bajo":
        query = query.filter(ClasificacionSRIE.confianza < 0.50)
    elif nivel == "medio":
        query = query.filter(ClasificacionSRIE.confianza >= 0.50, ClasificacionSRIE.confianza < 0.80)
    elif nivel == "alto":
        query = query.filter(ClasificacionSRIE.confianza >= 0.80)

    pagination = (
        query
        .options(
            db.joinedload(ClasificacionSRIE.pilar),
            db.joinedload(ClasificacionSRIE.participacion),
        )
        .order_by(ClasificacionSRIE.confianza.asc())
        .paginate(page=page, per_page=20, error_out=False)
    )
    return render_template("admin/clasificaciones.html", clasificaciones=pagination.items, pagination=pagination, nivel=nivel)


# ------------------------------------------------------------------
# Planes estratégicos
# ------------------------------------------------------------------
@admin_bp.route("/planes")
@login_required
def planes():
    planes = Plan.query.order_by(Plan.created_at.desc()).all()
    return render_template("admin/planes.html", planes=planes)


@admin_bp.route("/planes/<int:id>")
@login_required
def plan_detail(id):
    plan = Plan.query.get_or_404(id)
    pilares = Pilar.query.filter_by(plan_id=id).order_by(Pilar.orden).all()
    return render_template("admin/plan_detail.html", plan=plan, pilares=pilares)


@admin_bp.route("/planes/<int:id>/toggle", methods=["POST"])
@login_required
def plan_toggle(id):
    plan = Plan.query.get_or_404(id)
    plan.activo = not plan.activo
    db.session.commit()
    flash(f"Plan '{plan.nombre}' {'activado' if plan.activo else 'desactivado'}", "success")
    return redirect(url_for("admin.planes"))


# ------------------------------------------------------------------
# Export
# ------------------------------------------------------------------
@admin_bp.route("/export")
@login_required
def export_page():
    return render_template("admin/export.html")


@admin_bp.route("/export/csv")
@login_required
def export_csv():
    participaciones = Participacion.query.order_by(Participacion.created_at.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Departamento", "Municipio", "Zona", "Problemas", "Justificación", "Propuesta", "Actores", "Beneficiarios", "Fecha"])
    for p in participaciones:
        probs = ProblemaCatalogo.query.join(
            participacion_problemas, participacion_problemas.c.problema_id == ProblemaCatalogo.id,
        ).filter(participacion_problemas.c.participacion_id == p.id).all()
        acts = Actor.query.join(
            participacion_actores, participacion_actores.c.actor_id == Actor.id,
        ).filter(participacion_actores.c.participacion_id == p.id).all()
        bes = Beneficiario.query.join(
            participacion_beneficiarios, participacion_beneficiarios.c.beneficiario_id == Beneficiario.id,
        ).filter(participacion_beneficiarios.c.participacion_id == p.id).all()

        writer.writerow([
            p.id, p.departamento, p.municipio, p.zona,
            ", ".join([pr.nombre for pr in probs]),
            p.justificacion, p.propuesta,
            ", ".join([a.nombre for a in acts]),
            ", ".join([b.nombre for b in bes]),
            p.created_at.strftime("%Y-%m-%d %H:%M") if p.created_at else "",
        ])
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=participaciones.csv"},
    )


@admin_bp.route("/export/json")
@login_required
def export_json():
    participaciones = Participacion.query.order_by(Participacion.created_at.desc()).all()
    data = [p.to_dict() for p in participaciones]
    return Response(
        json.dumps(data, ensure_ascii=False, indent=2),
        mimetype="application/json",
        headers={"Content-Disposition": "attachment;filename=participaciones.json"},
    )


# ------------------------------------------------------------------
# Config
# ------------------------------------------------------------------
@admin_bp.route("/config")
@login_required
def config_page():
    config_data = {
        "plan_activo": Plan.query.filter_by(activo=True).first(),
        "total_planes": Plan.query.count(),
        "total_pilares": Pilar.query.count(),
        "total_sectores": Sector.query.count(),
        "total_subsectores": Subsector.query.count(),
        "total_problemas": ProblemaCatalogo.query.count(),
        "total_actores": Actor.query.count(),
        "total_beneficiarios": Beneficiario.query.count(),
        "rate_limit": current_app.config.get("RATELIMIT_DEFAULT", "N/A"),
    }
    return render_template("admin/config.html", config=config_data)


# ------------------------------------------------------------------
# Logs / Auditoría
# ------------------------------------------------------------------
@admin_bp.route("/logs")
@login_required
def logs():
    participaciones_recientes = (
        Participacion.query
        .order_by(Participacion.created_at.desc())
        .limit(50)
        .all()
    )
    return render_template("admin/logs.html", participaciones=participaciones_recientes)
