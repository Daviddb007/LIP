"""Blueprint del visor SECOP II público + servicio de licitación pública.

- `/secop` — visor de procesos de contratación pública con oferta abierta
  (métricas, filtros, tabla y gráficos Chart.js), con cross-ref a pilares SRIE.
- `/secop/api/datos` — JSON para gráficos.
- `/secop/licitar` — servicio comercial: ayudamos a empresas a licitar en lo
  público (formulario de lead con CSRF + rate limit + sanitización).
"""
from __future__ import annotations

from datetime import date, timedelta

from email_validator import EmailNotValidError, validate_email
from flask import Blueprint, flash, redirect, render_template, request, url_for

from app import cache, db, limiter
from app.models.secop import LeadSecop, SecopCorte, SecopProceso
from app.services.validation import sanitize_text

secop_bp = Blueprint("secop", __name__)


def _fmt_cop(valor: int) -> str:
    return f"${valor:,}".replace(",", ".")


def _corte_vigente() -> SecopCorte | None:
    return SecopCorte.query.order_by(SecopCorte.corte.desc()).first()


def _departamentos(corte) -> list[str]:
    rows = (
        db.session.query(SecopProceso.departamento)
        .filter_by(corte=corte)
        .distinct()
        .order_by(SecopProceso.departamento)
        .all()
    )
    return [r[0] for r in rows if r[0]]


def _modalidades(corte) -> list[str]:
    rows = (
        db.session.query(SecopProceso.modalidad)
        .filter_by(corte=corte)
        .distinct()
        .order_by(SecopProceso.modalidad)
        .all()
    )
    return [r[0] for r in rows if r[0]]


def _count_by(column, corte, limit=10) -> list[dict]:
    rows = (
        db.session.query(column, db.func.count(SecopProceso.id))
        .filter_by(corte=corte)
        .group_by(column)
        .order_by(db.func.count(SecopProceso.id).desc())
        .limit(limit)
        .all()
    )
    return [{"label": c or "Sin dato", "total": n} for c, n in rows]


def _pilares_counts(corte, limit=10) -> list[dict]:
    pilares: dict[str, int] = {}
    for (p,) in db.session.query(SecopProceso.pilares).filter_by(corte=corte).all():
        for slug in p or []:
            pilares[slug] = pilares.get(slug, 0) + 1
    top = sorted(pilares.items(), key=lambda kv: kv[1], reverse=True)[:limit]
    return [{"label": slug, "total": total} for slug, total in top]


def _stats(corte) -> dict:
    hoy = date.today()
    limite_7d = hoy + timedelta(days=7)
    base = SecopProceso.query.filter_by(corte=corte)
    total = base.count()
    valor_total = base.with_entities(db.func.coalesce(db.func.sum(SecopProceso.valor), 0)).scalar()
    return {
        "total": total,
        "valor_total": valor_total,
        "valor_promedio": round(valor_total / total) if total else 0,
        "entidades": base.with_entities(db.func.count(db.distinct(SecopProceso.entidad))).scalar(),
        "sin_rup": base.filter(SecopProceso.requiere_rup.is_(False)).count(),
        "vencen_7d": base.filter(SecopProceso.fecha_limite <= limite_7d).count(),
    }


def _query_filtrada(corte, q="", departamento="", modalidad="", requiere_rup="", pilar="", valor_min=None, valor_max=None):
    query = SecopProceso.query.filter_by(corte=corte)
    if q:
        like = f"%{q}%"
        query = query.filter(db.or_(SecopProceso.nombre.ilike(like), SecopProceso.entidad.ilike(like)))
    if departamento:
        query = query.filter(SecopProceso.departamento == departamento)
    if modalidad:
        query = query.filter(SecopProceso.modalidad == modalidad)
    if requiere_rup in ("1", "true", "si"):
        query = query.filter(SecopProceso.requiere_rup.is_(True))
    elif requiere_rup in ("0", "false", "no"):
        query = query.filter(SecopProceso.requiere_rup.is_(False))
    if pilar:
        query = query.filter(db.cast(SecopProceso.pilares, db.String).ilike(f'%"{pilar}"%'))
    if valor_min is not None:
        query = query.filter(SecopProceso.valor >= valor_min)
    if valor_max is not None:
        query = query.filter(SecopProceso.valor <= valor_max)
    return query


@secop_bp.route("/secop")
@cache.cached(timeout=60, query_string=True)
def pagina():
    corte_obj = _corte_vigente()
    if not corte_obj or SecopProceso.query.filter_by(corte=corte_obj.corte).count() == 0:
        return render_template("secop.html", vacio=True)

    corte = corte_obj.corte
    q = request.args.get("q", "").strip()
    departamento = request.args.get("departamento", "").strip()
    modalidad = request.args.get("modalidad", "").strip()
    requiere_rup = request.args.get("rup", "").strip()
    pilar = request.args.get("pilar", "").strip()
    valor_min = request.args.get("valor_min", type=int)
    valor_max = request.args.get("valor_max", type=int)
    page = request.args.get("page", 1, type=int)

    query = _query_filtrada(corte, q, departamento, modalidad, requiere_rup, pilar, valor_min, valor_max)
    pagination = query.order_by(
        SecopProceso.fecha_limite.asc(), SecopProceso.valor.desc()
    ).paginate(page=page, per_page=25, error_out=False)

    hoy = date.today()
    rows = []
    for p in pagination.items:
        d = p.to_dict()
        d["dl"] = (p.fecha_limite - hoy).days
        d["valor_fmt"] = _fmt_cop(p.valor)
        d["fecha_fmt"] = p.fecha_limite.strftime("%d/%m/%Y")
        rows.append(d)

    stats = _stats(corte)
    context = {
        "vacio": False,
        "corte": corte,
        "corte_legible": f"{corte.day} {['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic'][corte.month - 1]} {corte.year}",
        "generado": corte_obj.generado_at.strftime("%d/%m/%Y"),
        "stats": stats,
        "stats_fmt": {
            "valor_total": _fmt_cop(stats["valor_total"]),
            "valor_promedio": _fmt_cop(stats["valor_promedio"]),
        },
        "chart_departamentos": _count_by(SecopProceso.departamento, corte),
        "chart_modalidades": _count_by(SecopProceso.modalidad, corte),
        "chart_tipos": _count_by(SecopProceso.tipo_contrato, corte),
        "chart_pilares": _pilares_counts(corte),
        "departamentos": _departamentos(corte),
        "modalidades": _modalidades(corte),
        "filtros": {"q": q, "departamento": departamento, "modalidad": modalidad, "rup": requiere_rup, "pilar": pilar,
                    "valor_min": valor_min or "", "valor_max": valor_max or ""},
        "rows": rows,
        "pagination": pagination,
    }
    return render_template("secop.html", **context)


@secop_bp.route("/secop/api/datos")
@cache.cached(timeout=60, query_string=True)
def api_datos():
    from flask import jsonify

    corte_obj = _corte_vigente()
    if not corte_obj:
        return jsonify({"vacio": True, "data": []})
    corte = corte_obj.corte
    return jsonify({
        "vacio": False,
        "corte": corte.isoformat(),
        "total": SecopProceso.query.filter_by(corte=corte).count(),
        "departamentos": _count_by(SecopProceso.departamento, corte),
        "modalidades": _count_by(SecopProceso.modalidad, corte),
        "tipos": _count_by(SecopProceso.tipo_contrato, corte),
        "pilares": _pilares_counts(corte),
    })


@secop_bp.route("/secop/api/procesos")
@cache.cached(timeout=60)
def api_procesos():
    """Todos los procesos del corte en formato compacto (visor interactivo)."""
    from flask import jsonify

    corte_obj = _corte_vigente()
    if not corte_obj:
        return jsonify([])
    corte = corte_obj.corte
    rows = (
        SecopProceso.query.filter_by(corte=corte)
        .order_by(SecopProceso.fecha_limite.asc())
        .all()
    )
    out = [
        {
            "e": p.entidad,
            "d": p.departamento,
            "c": p.ciudad,
            "n": p.nombre,
            "m": p.modalidad,
            "t": p.tipo_contrato,
            "v": p.valor,
            "rup": p.requiere_rup,
            "dl": (p.fecha_limite - date.today()).days,
            "f": p.fecha_limite.isoformat(),
            "u": p.url,
            "tm": p.temas,
            "pil": p.pilares,
        }
        for p in rows
    ]
    return jsonify(out)


@secop_bp.route("/secop/licitar", methods=["GET", "POST"])
@limiter.limit("20 per minute;200 per hour")
def licitar():
    if request.method == "POST":
        nombre = sanitize_text(request.form.get("nombre", ""))[:120]
        empresa = sanitize_text(request.form.get("empresa", ""))[:160]
        email = sanitize_text(request.form.get("email", ""))[:160]
        telefono = sanitize_text(request.form.get("telefono", ""))[:40]
        sector = sanitize_text(request.form.get("sector", ""))[:160]
        estado_rup = sanitize_text(request.form.get("estado_rup", ""))[:60]
        mensaje = sanitize_text(request.form.get("mensaje", ""))[:1000]

        errores: list[str] = []
        if len(nombre) < 2:
            errores.append("Escribe tu nombre")
        if len(empresa) < 2:
            errores.append("Escribe el nombre de tu empresa")
        try:
            validate_email(email, check_deliverability=False)
        except EmailNotValidError:
            errores.append("El correo electrónico no es válido")
        if len(telefono) < 6:
            errores.append("Escribe un teléfono de contacto válido")

        for e in errores:
            flash(e, "error")
        if errores:
            return render_template(
                "secop_licitar.html",
                form_vals={"nombre": nombre, "empresa": empresa, "email": email, "telefono": telefono, "sector": sector, "estado_rup": estado_rup, "mensaje": mensaje},
            ), 400

        db.session.add(LeadSecop(
            nombre=nombre,
            empresa=empresa,
            email=email,
            telefono=telefono,
            sector=sector or None,
            estado_rup=estado_rup or None,
            mensaje=mensaje or None,
        ))
        db.session.commit()
        flash(
            "¡Recibido! Un profesional de licitación pública de nuestro equipo te contactará en menos de 24 horas.",
            "success",
        )
        return redirect(url_for("secop.licitar"))

    return render_template("secop_licitar.html", form_vals={})
