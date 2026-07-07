from flask import Blueprint, jsonify, render_template

from app.services.analitica_service import obtener_analitica

analitica_bp = Blueprint('analitica', __name__)


@analitica_bp.route('/analitica')
def pagina():
    return render_template('analitica.html')


@analitica_bp.route('/api/analitica')
def api_analitica():
    return jsonify(obtener_analitica())
