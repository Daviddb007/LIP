"""Blueprint de Grupos Focales (fase "Estrategia de participación robusta").

Todo el módulo vive bajo /admin/focales (reserva total de la información):
organizaciones, sesiones, participantes, preguntas, audios, transcripción y
visor del grafo de conocimiento.
"""
from __future__ import annotations

import hashlib
import os
import uuid
from datetime import datetime, timezone

from flask import (
    Blueprint, current_app, flash, jsonify, redirect, render_template, request,
    send_file, session, url_for,
)

from app import db
from app.decorators import login_required
from app.models.catalog import Sector
from app.models.focal import (
    AudioFocal, OrgFocal, ParticipanteFocal, PreguntaFocal, SesionFocal,
)
from app.services import grafo_service
from app.services.worker_jobs import encolar_grafo, encolar_transcripcion

focales_bp = Blueprint("focales", __name__, url_prefix="/admin/focales")


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _parse_int(valor: str | None) -> int | None:
    if not valor:
        return None
    try:
        return int(valor)
    except (TypeError, ValueError):
        return None


def _admin_actual() -> str | None:
    return session.get("admin_user") or session.get("admin_login", "")


# ---------------------------------------------------------------------------
# Organizaciones
# ---------------------------------------------------------------------------

@focales_bp.route("/organizaciones")
@login_required
def organizaciones():
    search = request.args.get("q", "").strip()
    query = OrgFocal.query
    if search:
        query = query.filter(OrgFocal.nombre.ilike(f"%{search}%"))
    orgs = query.order_by(OrgFocal.nombre).all()
    return render_template("admin/focales/organizaciones.html", orgs=orgs, search=search)


@focales_bp.route("/organizaciones/nueva", methods=["GET", "POST"])
@login_required
def organizacion_nueva():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        if not nombre:
            flash("El nombre es obligatorio", "error")
            return redirect(url_for("focales.organizacion_nueva"))
        if OrgFocal.query.filter_by(nombre=nombre).first():
            flash(f"Ya existe una organización llamada '{nombre}'", "error")
            return redirect(url_for("focales.organizacion_nueva"))

        org = OrgFocal(
            nombre=nombre,
            tipo=request.form.get("tipo", "gremio"),
            sector_id=_parse_int(request.form.get("sector_id")),
            descripcion=request.form.get("descripcion", "").strip() or None,
            contacto_nombre=request.form.get("contacto_nombre", "").strip() or None,
            contacto_email=request.form.get("contacto_email", "").strip() or None,
            contacto_telefono=request.form.get("contacto_telefono", "").strip() or None,
        )
        db.session.add(org)
        db.session.commit()
        flash(f"Organización '{org.nombre}' creada", "success")
        return redirect(url_for("focales.organizaciones"))

    sectores = Sector.query.filter_by(activo=True).order_by(Sector.orden).all()
    return render_template("admin/focales/organizacion_form.html", org=None, sectores=sectores)


@focales_bp.route("/organizaciones/<int:org_id>")
@login_required
def organizacion_detalle(org_id: int):
    org = OrgFocal.query.get_or_404(org_id)
    return render_template("admin/focales/organizacion_detalle.html", org=org)


@focales_bp.route("/organizaciones/<int:org_id>/toggle", methods=["POST"])
@login_required
def organizacion_toggle(org_id: int):
    org = OrgFocal.query.get_or_404(org_id)
    org.activo = not org.activo
    db.session.commit()
    flash(f"Organización '{org.nombre}' {'activada' if org.activo else 'desactivada'}", "success")
    return redirect(url_for("focales.organizaciones"))


@focales_bp.route("/organizaciones/<int:org_id>/eliminar", methods=["POST"])
@login_required
def organizacion_eliminar(org_id: int):
    org = OrgFocal.query.get_or_404(org_id)
    for sesion in org.sesiones:
        _limpiar_audios_sesion(sesion.id)
    db.session.delete(org)
    db.session.commit()
    flash(f"Organización '{org.nombre}' eliminada", "success")
    return redirect(url_for("focales.organizaciones"))


# ---------------------------------------------------------------------------
# Sesiones
# ---------------------------------------------------------------------------

@focales_bp.route("/sesiones")
@login_required
def sesiones():
    estado = request.args.get("estado", "").strip()
    org_id = request.args.get("org", type=int)
    query = SesionFocal.query
    if estado:
        query = query.filter(SesionFocal.estado == estado)
    if org_id:
        query = query.filter(SesionFocal.org_id == org_id)
    items = query.order_by(SesionFocal.fecha.desc()).all()
    orgs = OrgFocal.query.filter_by(activo=True).order_by(OrgFocal.nombre).all()
    return render_template(
        "admin/focales/sesiones.html",
        sesiones=items, orgs=orgs, filtro_estado=estado, filtro_org=org_id,
    )


@focales_bp.route("/sesiones/nueva", methods=["GET", "POST"])
@login_required
def sesion_nueva():
    org_id = request.args.get("org_id", type=int)
    if request.method == "POST":
        org_id = int(request.form.get("org_id", "0"))
        org = OrgFocal.query.get(org_id)
        if not org:
            flash("Seleccione una organización válida", "error")
            return redirect(url_for("focales.sesion_nueva", org_id=org_id))

        fecha = request.form.get("fecha", "").strip()
        try:
            from datetime import date

            fecha_parsed = date.fromisoformat(fecha)
        except ValueError:
            flash("Fecha inválida. Use formato AAAA-MM-DD", "error")
            return redirect(url_for("focales.sesion_nueva", org_id=org_id))

        sesion = SesionFocal(
            org_id=org.id,
            titulo=request.form.get("titulo", "").strip() or f"Sesión con {org.nombre}",
            fecha=fecha_parsed,
            modalidad=request.form.get("modalidad", "presencial"),
            lugar=request.form.get("lugar", "").strip() or None,
            objetivo=request.form.get("objetivo", "").strip() or None,
            estado=request.form.get("estado", "programada"),
        )
        db.session.add(sesion)
        db.session.commit()
        flash(f"Sesión '{sesion.titulo}' creada", "success")
        return redirect(url_for("focales.sesion_detalle", sesion_id=sesion.id))

    orgs = OrgFocal.query.filter_by(activo=True).order_by(OrgFocal.nombre).all()
    return render_template(
        "admin/focales/sesion_form.html", sesion=None, orgs=orgs, org_id=org_id,
    )


@focales_bp.route("/sesiones/<int:sesion_id>")
@login_required
def sesion_detalle(sesion_id: int):
    sesion = SesionFocal.query.get_or_404(sesion_id)
    sectores = Sector.query.filter_by(activo=True).order_by(Sector.orden).all()
    return render_template(
        "admin/focales/sesion_detalle.html",
        sesion=sesion, sectores=sectores,
        extensiones=list(current_app.config["AUDIO_ALLOWED_EXTENSIONS"]),
        max_mb=current_app.config["UPLOAD_MAX_MB"],
    )


@focales_bp.route("/sesiones/<int:sesion_id>/estado", methods=["POST"])
@login_required
def sesion_estado(sesion_id: int):
    sesion = SesionFocal.query.get_or_404(sesion_id)
    nuevo = request.form.get("estado", "")
    if nuevo in dict(SesionFocal.ESTADOS):
        sesion.estado = nuevo
        sesion.updated_at = _now()
        db.session.commit()
        flash(f"Sesión marcada como '{nuevo}'", "success")
    return redirect(url_for("focales.sesion_detalle", sesion_id=sesion.id))


@focales_bp.route("/sesiones/<int:sesion_id>/eliminar", methods=["POST"])
@login_required
def sesion_eliminar(sesion_id: int):
    sesion = SesionFocal.query.get_or_404(sesion_id)
    org_id = sesion.org_id
    _limpiar_audios_sesion(sesion.id)
    db.session.delete(sesion)
    db.session.commit()
    flash("Sesión eliminada", "success")
    return redirect(url_for("focales.organizacion_detalle", org_id=org_id))


# ---------------------------------------------------------------------------
# Participantes
# ---------------------------------------------------------------------------

@focales_bp.route("/sesiones/<int:sesion_id>/participantes", methods=["POST"])
@login_required
def participante_nuevo(sesion_id: int):
    sesion = SesionFocal.query.get_or_404(sesion_id)
    nombre = request.form.get("nombre", "").strip()
    if not nombre:
        flash("El nombre del participante es obligatorio", "error")
        return redirect(url_for("focales.sesion_detalle", sesion_id=sesion.id))

    consentimiento = request.form.get("consentimiento_1581") == "on"
    participante = ParticipanteFocal(
        sesion_id=sesion.id,
        nombre=nombre,
        cargo=request.form.get("cargo", "").strip() or None,
        email=request.form.get("email", "").strip() or None,
        telefono=request.form.get("telefono", "").strip() or None,
        consentimiento_aceptado=consentimiento,
        consentimiento_version=current_app.config.get("CONSENT_VERSION", "2026-01"),
        consentimiento_at=_now() if consentimiento else None,
    )
    db.session.add(participante)
    db.session.commit()
    flash(f"Participante '{nombre}' registrado", "success")
    return redirect(url_for("focales.sesion_detalle", sesion_id=sesion.id))


@focales_bp.route("/participantes/<int:p_id>/eliminar", methods=["POST"])
@login_required
def participante_eliminar(p_id: int):
    p = ParticipanteFocal.query.get_or_404(p_id)
    sesion_id = p.sesion_id
    db.session.delete(p)
    db.session.commit()
    flash("Participante eliminado", "success")
    return redirect(url_for("focales.sesion_detalle", sesion_id=sesion_id))


# ---------------------------------------------------------------------------
# Preguntas
# ---------------------------------------------------------------------------

@focales_bp.route("/sesiones/<int:sesion_id>/preguntas", methods=["POST"])
@login_required
def pregunta_nueva(sesion_id: int):
    sesion = SesionFocal.query.get_or_404(sesion_id)
    texto = request.form.get("texto", "").strip()
    if not texto:
        flash("El texto de la pregunta es obligatorio", "error")
        return redirect(url_for("focales.sesion_detalle", sesion_id=sesion.id))

    siguiente_orden = (max([p.orden for p in sesion.preguntas], default=0) + 1)
    pregunta = PreguntaFocal(
        sesion_id=sesion.id,
        categoria=request.form.get("categoria", "problema"),
        texto=texto,
        orden=siguiente_orden,
    )
    db.session.add(pregunta)
    db.session.commit()
    flash("Pregunta añadida", "success")
    return redirect(url_for("focales.sesion_detalle", sesion_id=sesion.id))


@focales_bp.route("/preguntas/<int:p_id>/eliminar", methods=["POST"])
@login_required
def pregunta_eliminar(p_id: int):
    p = PreguntaFocal.query.get_or_404(p_id)
    sesion_id = p.sesion_id
    db.session.delete(p)
    db.session.commit()
    flash("Pregunta eliminada", "success")
    return redirect(url_for("focales.sesion_detalle", sesion_id=sesion_id))


# ---------------------------------------------------------------------------
# Audios (almacenamiento reservado + cola de transcripción)
# ---------------------------------------------------------------------------

def _directorio_audios(sesion_id: int) -> str:
    directorio = os.path.join(current_app.config["UPLOADS_DIR"], f"sesion_{sesion_id}")
    os.makedirs(directorio, exist_ok=True)
    return directorio


def _limpiar_audios_sesion(sesion_id: int) -> None:
    """Elimina del disco el directorio de audios de una sesión (archivos reservados)."""
    directorio = os.path.join(current_app.config["UPLOADS_DIR"], f"sesion_{sesion_id}")
    if os.path.isdir(directorio):
        import shutil

        shutil.rmtree(directorio, ignore_errors=True)


def _sha256_archivo(ruta: str) -> str:
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(65536), b""):
            h.update(bloque)
    return h.hexdigest()


@focales_bp.route("/sesiones/<int:sesion_id>/audios", methods=["POST"])
@login_required
def audio_subir(sesion_id: int):
    sesion = SesionFocal.query.get_or_404(sesion_id)
    archivo = request.files.get("archivo")
    if not archivo or not archivo.filename:
        flash("Seleccione un archivo de audio", "error")
        return redirect(url_for("focales.sesion_detalle", sesion_id=sesion.id))

    ext = os.path.splitext(archivo.filename)[1].lower()
    permitidas = current_app.config["AUDIO_ALLOWED_EXTENSIONS"]
    if ext not in permitidas:
        flash(f"Formato no permitido. Permitidos: {', '.join(permitidas)}", "error")
        return redirect(url_for("focales.sesion_detalle", sesion_id=sesion.id))

    archivo.seek(0, os.SEEK_END)
    tamano = archivo.tell()
    archivo.seek(0)
    max_bytes = current_app.config["UPLOAD_MAX_MB"] * 1024 * 1024
    if tamano > max_bytes:
        flash(f"El archivo supera el máximo de {current_app.config['UPLOAD_MAX_MB']} MB", "error")
        return redirect(url_for("focales.sesion_detalle", sesion_id=sesion.id))

    nombre_uuid = f"{uuid.uuid4().hex}{ext}"
    ruta = os.path.join(_directorio_audios(sesion.id), nombre_uuid)
    archivo.save(ruta)

    audio = AudioFocal(
        sesion_id=sesion.id,
        nombre_original=archivo.filename,
        ruta_archivo=os.path.abspath(ruta),
        tamano_bytes=tamano,
        formato=ext.lstrip("."),
        sha256=_sha256_archivo(ruta),
        estado="pendiente",
        creado_por=_admin_actual(),
    )
    db.session.add(audio)
    db.session.commit()

    job_id = encolar_transcripcion(audio.id)
    if job_id:
        audio.estado = "en_cola"
        db.session.commit()
        flash(f"Audio '{archivo.filename}' subido y encolado para transcripción", "success")
    else:
        flash(
            "Audio subido. No se pudo encolar (¿Redis activo?). "
            "Quedó pendiente; usa `flask transcribir-pendientes` para procesarlo.",
            "warning",
        )
    return redirect(url_for("focales.sesion_detalle", sesion_id=sesion.id))


@focales_bp.route("/audios/<int:audio_id>/descargar")
@login_required
def audio_descargar(audio_id: int):
    audio = AudioFocal.query.get_or_404(audio_id)
    base = os.path.realpath(current_app.config["UPLOADS_DIR"])
    ruta = os.path.realpath(audio.ruta_archivo)
    if not ruta.startswith(base):
        flash("Ruta no válida", "error")
        return redirect(url_for("focales.sesion_detalle", sesion_id=audio.sesion_id))
    if not os.path.exists(ruta):
        flash("El archivo ya no existe en el servidor", "error")
        return redirect(url_for("focales.sesion_detalle", sesion_id=audio.sesion_id))
    return send_file(ruta, as_attachment=True, download_name=audio.nombre_original)


@focales_bp.route("/audios/<int:audio_id>/reprocesar", methods=["POST"])
@login_required
def audio_reprocesar(audio_id: int):
    audio = AudioFocal.query.get_or_404(audio_id)
    if audio.estado == "transcrito":
        flash("El audio ya está transcrito. Para re-transcribir se reconstruiría el transcript.", "info")
        return redirect(url_for("focales.sesion_detalle", sesion_id=audio.sesion_id))
    audio.estado = "pendiente"
    audio.error_mensaje = None
    db.session.commit()
    job_id = encolar_transcripcion(audio.id)
    if job_id:
        audio.estado = "en_cola"
        db.session.commit()
        flash("Audio reencolado para transcripción", "success")
    else:
        flash("Audio marcado pendiente (Redis no disponible)", "warning")
    return redirect(url_for("focales.sesion_detalle", sesion_id=audio.sesion_id))


@focales_bp.route("/audios/<int:audio_id>/eliminar", methods=["POST"])
@login_required
def audio_eliminar(audio_id: int):
    audio = AudioFocal.query.get_or_404(audio_id)
    sesion_id = audio.sesion_id
    try:
        if audio.ruta_archivo and os.path.exists(audio.ruta_archivo):
            os.remove(audio.ruta_archivo)
    except OSError:
        pass
    db.session.delete(audio)
    db.session.commit()
    flash("Audio eliminado", "success")
    return redirect(url_for("focales.sesion_detalle", sesion_id=sesion_id))


# ---------------------------------------------------------------------------
# Transcripción y Grafo
# ---------------------------------------------------------------------------

@focales_bp.route("/sesiones/<int:sesion_id>/grafo/construir", methods=["POST"])
@login_required
def grafo_construir(sesion_id: int):
    sesion = SesionFocal.query.get_or_404(sesion_id)
    if not sesion.transcript:
        flash("La sesión aún no tiene transcripción", "error")
        return redirect(url_for("focales.sesion_detalle", sesion_id=sesion.id))

    job_id = encolar_grafo(sesion.id)
    if job_id:
        flash("Construcción del grafo encolada", "success")
    else:
        resultado = grafo_service.construir_grafo(sesion.transcript.id)
        if resultado["ok"]:
            flash(f"Grafo construido: {resultado['nodos']} nodos", "success")
        else:
            flash(resultado.get("error", "Error al construir el grafo"), "error")
    return redirect(url_for("focales.sesion_detalle", sesion_id=sesion.id))


@focales_bp.route("/sesiones/<int:sesion_id>/grafo")
@login_required
def grafo_ver(sesion_id: int):
    sesion = SesionFocal.query.get_or_404(sesion_id)
    return render_template("admin/focales/grafo.html", sesion=sesion)


@focales_bp.route("/api/sesiones/<int:sesion_id>/grafo")
@login_required
def api_grafo(sesion_id: int):
    sesion = SesionFocal.query.get_or_404(sesion_id)
    return jsonify(grafo_service.datos_grafo(sesion.id))


@focales_bp.route("/sesiones/<int:sesion_id>/grafo/exportar")
@login_required
def grafo_exportar(sesion_id: int):
    sesion = SesionFocal.query.get_or_404(sesion_id)
    html = grafo_service.exportar_html(sesion.id)
    from flask import Response

    return Response(
        html,
        mimetype="text/html",
        headers={"Content-Disposition": f"attachment;filename=grafo_sesion_{sesion.id}.html"},
    )


@focales_bp.route("/sesiones/<int:sesion_id>/transcript")
@login_required
def transcript_ver(sesion_id: int):
    sesion = SesionFocal.query.get_or_404(sesion_id)
    transcript = sesion.transcript
    if not transcript:
        flash("La sesión aún no tiene transcripción", "error")
        return redirect(url_for("focales.sesion_detalle", sesion_id=sesion.id))
    return render_template("admin/focales/transcript.html", sesion=sesion, transcript=transcript)
