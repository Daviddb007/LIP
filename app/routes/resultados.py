from flask import Blueprint, render_template, jsonify

from app import cache
from app.services.stats_service import get_estadisticas_completas

resultados_bp = Blueprint('resultados', __name__)


@resultados_bp.route('/resultados')
def resultados():
    """Render public results dashboard."""
    return render_template('resultados.html')


@resultados_bp.route('/api/estadisticas')
@cache.cached(timeout=300, query_string=True)
def api_estadisticas():
    """Return full participation statistics as JSON.

    Cached for 5 minutes to reduce database load.
    """
    return jsonify(get_estadisticas_completas())
