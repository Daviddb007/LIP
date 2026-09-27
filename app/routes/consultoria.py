"""Ruta de la línea de consultoría para entidades públicas.

`/consultoria` — servicio: diagnóstico e inteligencia para municipios,
departamentos y entidades centralizadas. Formulario de lead con CSRF + rate
limit + sanitización.
"""
from __future__ import annotations

from email_validator import EmailNotValidError, validate_email
from flask import Blueprint, flash, redirect, render_template, request, url_for

from app import db, limiter
from app.models.consultoria import LeadConsultoria
from app.services.validation import sanitize_text

consultoria_bp = Blueprint("consultoria", __name__)


@consultoria_bp.route("/consultoria", methods=["GET", "POST"])
@limiter.limit("20 per minute;200 per hour")
def pagina():
    if request.method == "POST":
        nombre = sanitize_text(request.form.get("nombre", ""))[:120]
        entidad = sanitize_text(request.form.get("entidad", ""))[:200]
        cargo = sanitize_text(request.form.get("cargo", ""))[:120]
        email = sanitize_text(request.form.get("email", ""))[:160]
        telefono = sanitize_text(request.form.get("telefono", ""))[:40]
        tipo_entidad = sanitize_text(request.form.get("tipo_entidad", "municipio"))[:60]
        necesidad = sanitize_text(request.form.get("necesidad", ""))[:160]
        mensaje = sanitize_text(request.form.get("mensaje", ""))[:1500]

        errores: list[str] = []
        if len(nombre) < 2:
            errores.append("Escribe tu nombre")
        if len(entidad) < 3:
            errores.append("Escribe el nombre de la entidad")
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
                "consultoria.html",
                form_vals={"nombre": nombre, "entidad": entidad, "cargo": cargo, "email": email, "telefono": telefono,
                           "tipo_entidad": tipo_entidad, "necesidad": necesidad, "mensaje": mensaje},
            ), 400

        db.session.add(LeadConsultoria(
            nombre=nombre,
            entidad=entidad,
            cargo=cargo or None,
            email=email,
            telefono=telefono,
            tipo_entidad=tipo_entidad,
            necesidad=necesidad or None,
            mensaje=mensaje or None,
        ))
        db.session.commit()
        flash(
            "Recibimos tu solicitud. Un consultor de inteligencia pública te contactará en menos de 24 horas.",
            "success",
        )
        return redirect(url_for("consultoria.pagina"))

    return render_template("consultoria.html", form_vals={})
