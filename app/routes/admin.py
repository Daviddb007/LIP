from flask import (
    Blueprint, render_template, request, jsonify,
    session, redirect, url_for, current_app,
)
from werkzeug.security import check_password_hash

from app import db, limiter
from app.decorators import login_required
from app.forms import LoginForm
from app.models.participacion import Participacion
from app.models.sector import Sector
from app.services.stats_service import get_estadisticas_completas
from app.services.export_service import exportar_participaciones_csv
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login():
    """Admin login with credential validation and CSRF protection."""

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        if not _credentials_valid(username, password):
            return render_template('admin/login.html', form=form, error='Credenciales inválidas')

        session.clear()
        session['admin_logged_in'] = True
        session.permanent = True
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/login.html', form=form)


def _credentials_valid(username: str, password: str) -> bool:
    """Check admin credentials against app config.

    Supports both hashed passwords (pbkdf2:sha256) and legacy plaintext
    for backward compatibility. Legacy passwords should be migrated.
    """
    config_user = current_app.config['ADMIN_USER']
    config_pass = current_app.config['ADMIN_PASS']

    if username != config_user:
        return False

    if config_pass.startswith('pbkdf2:'):
        return check_password_hash(config_pass, password)

    return password == config_pass


@admin_bp.route('/logout')
def logout():
    """Clear admin session and redirect to login."""
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin.login'))


@admin_bp.route('/')
@login_required
def dashboard():
    """Render admin dashboard with participation stats."""
    stats = get_estadisticas_completas()
    sectores_stats = _get_sectores_stats()
    departamentos_stats = _get_departamentos_stats()

    return render_template(
        'admin/dashboard.html',
        total_participaciones=stats['total_participaciones'],
        total_departamentos=stats['total_departamentos'],
        sectores_stats=sectores_stats,
        departamentos_stats=departamentos_stats,
    )


def _get_sectores_stats() -> list:
    """Count participations per sector, ordered by frequency."""
    return (
        db.session.query(Sector.nombre, func.count(Participacion.id))
        .join(Participacion.sectores)
        .group_by(Sector.nombre)
        .order_by(func.count(Participacion.id).desc())
        .all()
    )


def _get_departamentos_stats() -> list:
    """Count participations per department, ordered by frequency."""
    return (
        db.session.query(
            Participacion.departamento, func.count(Participacion.id)
        )
        .filter(
            Participacion.departamento.isnot(None),
            Participacion.departamento != '',
        )
        .group_by(Participacion.departamento)
        .order_by(func.count(Participacion.id).desc())
        .all()
    )


@admin_bp.route('/api/participaciones')
@login_required
def api_participaciones():
    """Return paginated participations with optional filters."""
    filters = _extract_filters()
    participaciones = Participacion.find_paginated(**filters)

    return jsonify({
        'participaciones': [p.to_admin_dict() for p in participaciones.items],
        'total': participaciones.total,
        'pages': participaciones.pages,
        'current_page': participaciones.page,
    })


def _extract_filters() -> dict:
    """Extract and sanitize query parameters for participation filtering."""
    return {
        'departamento': request.args.get('departamento', '').strip() or None,
        'sector': request.args.get('sector', '').strip() or None,
        'rango_edad': request.args.get('rango_edad', '').strip() or None,
        'genero': request.args.get('genero', '').strip() or None,
        'busqueda': request.args.get('busqueda', '').strip() or None,
        'page': request.args.get('page', 1, type=int),
        'per_page': request.args.get('per_page', 50, type=int),
    }


@admin_bp.route('/api/participaciones/<int:participacion_id>')
@login_required
def api_participacion_detalle(participacion_id: int):
    """Return a single participation by ID."""
    participacion = Participacion.query.get_or_404(participacion_id)
    return jsonify(participacion.to_admin_dict())


@admin_bp.route('/api/exportar')
@login_required
def api_exportar():
    """Export all participations as a CSV download."""
    csv_content = exportar_participaciones_csv()
    return csv_content, 200, {
        'Content-Type': 'text/csv',
        'Content-Disposition': 'attachment; filename=participaciones.csv',
    }
