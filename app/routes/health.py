"""Blueprint de health check."""
from flask import Blueprint, jsonify

from app import db, limiter

health_bp = Blueprint("health", __name__)


@health_bp.route("/health")
@limiter.exempt
def health_check():
    """Verifica conectividad con la base de datos."""
    try:
        db.session.execute(db.text("SELECT 1"))
        return jsonify({"status": "healthy", "database": "connected"})
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 503
