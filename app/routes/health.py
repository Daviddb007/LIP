from flask import Blueprint, jsonify

from app import db, limiter

health_bp = Blueprint('health', __name__)


@health_bp.route('/health')
@limiter.exempt
def health_check():
    """Health check endpoint for monitoring and load balancers."""
    try:
        db.session.execute(db.text('SELECT 1'))
        db_status = 'healthy'
    except Exception:
        db_status = 'unhealthy'

    status = 'healthy' if db_status == 'healthy' else 'degraded'
    status_code = 200 if status == 'healthy' else 503

    return jsonify({
        'status': status,
        'database': db_status,
    }), status_code
