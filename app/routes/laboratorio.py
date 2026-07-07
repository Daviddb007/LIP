from flask import Blueprint, jsonify, render_template, request

from app.services.laboratorio_service import estado_actual, simular

laboratorio_bp = Blueprint('laboratorio', __name__)


@laboratorio_bp.route('/laboratorio')
def pagina():
    return render_template('laboratorio.html')


@laboratorio_bp.route('/api/laboratorio/estado')
def api_estado():
    return jsonify(estado_actual())


@laboratorio_bp.route('/api/laboratorio/simular', methods=['POST'])
def api_simular():
    params = request.get_json(silent=True) or {}
    return jsonify(simular(params))
