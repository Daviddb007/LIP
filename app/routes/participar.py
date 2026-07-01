from flask import Blueprint, render_template, request, jsonify

from app import db, limiter
from app.errors import ValidationError, RateLimitError, DatabaseError
from app.models.participacion import Participacion
from app.models.sector import Sector
from app.models.problema import Problema
from app.decorators import get_client_ip
from app.services.validation import validate_participacion
from app.services.participacion_service import crear_participacion

participar_bp = Blueprint('participar', __name__)


@participar_bp.route('/participar')
def participar():
    """Render the participation form with active sectors."""
    sectores = Sector.find_active()
    return render_template('participar.html', sectores=sectores)


@participar_bp.route('/api/sectores')
def api_sectores():
    """Return active sectors as JSON."""
    sectores = Sector.find_active()
    return jsonify([s.to_dict() for s in sectores])


@participar_bp.route('/api/problemas/<int:sector_id>')
def api_problemas(sector_id: int):
    """Return active problems for a given sector."""
    problemas = Problema.find_active_by_sector(sector_id)
    return jsonify([{'id': p.id, 'nombre': p.nombre} for p in problemas])


@participar_bp.route('/api/enviar', methods=['POST'])
@limiter.limit("5 per minute")
def api_enviar():
    """Submit a new participation with validation and rate limiting."""
    client_ip = get_client_ip()

    data = request.get_json(silent=True)
    if not data:
        raise ValidationError('Datos JSON requeridos')

    validate_participacion(data)
    participacion = crear_participacion(data, client_ip)

    return jsonify({
        'success': True,
        'message': 'Participación registrada exitosamente',
        'id': participacion.id,
    })


@participar_bp.route('/confirmacion')
def confirmacion():
    """Render the confirmation page after successful submission."""
    return render_template('confirmacion.html')
