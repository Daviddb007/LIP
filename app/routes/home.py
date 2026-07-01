from flask import Blueprint, render_template

from app import cache
from app.services.stats_service import get_estadisticas_generales

home_bp = Blueprint('home', __name__)


@home_bp.route('/')
@cache.cached(timeout=300)
def index():
    """Render home page with high-level stats.

    Cached for 5 minutes to reduce database load.
    """
    stats = get_estadisticas_generales()
    return render_template('home.html', **stats)
