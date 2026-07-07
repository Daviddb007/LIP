from flask import Blueprint, jsonify, render_template, request

from app.models.politica import Politica
from app.models.sector import Sector
from app.services.srie_service import clasificar

biblioteca_bp = Blueprint('biblioteca', __name__)


@biblioteca_bp.route('/biblioteca')
def lista():
    sectores = Sector.find_active()
    estado_filter = request.args.get('estado', '')
    sector_filter = request.args.get('sector', '')

    query = Politica.query.filter_by(activo=True)

    if estado_filter:
        query = query.filter(Politica.estado == estado_filter)
    if sector_filter:
        query = query.filter(Politica.sector_id == int(sector_filter))

    politicas = query.order_by(Politica.created_at.desc()).all()

    return render_template(
        'biblioteca.html',
        politicas=politicas,
        sectores=sectores,
        estado_filter=estado_filter,
        sector_filter=sector_filter,
    )


@biblioteca_bp.route('/biblioteca/<int:politica_id>')
def detalle(politica_id):
    politica = Politica.query.get_or_404(politica_id)
    return render_template('biblioteca_detalle.html', politica=politica)


@biblioteca_bp.route('/api/politicas')
def api_lista():
    politicas = Politica.query.filter_by(activo=True).order_by(Politica.created_at.desc()).all()
    return jsonify([p.to_dict() for p in politicas])


@biblioteca_bp.route('/api/politicas/<int:politica_id>')
def api_detalle(politica_id):
    politica = Politica.query.get_or_404(politica_id)
    return jsonify(politica.to_dict())


@biblioteca_bp.route('/api/politicas/<int:politica_id>/preguntar', methods=['POST'])
def api_preguntar(politica_id):
    politica = Politica.query.get_or_404(politica_id)
    data = request.get_json(silent=True)
    pregunta = (data or {}).get('pregunta', '')

    datos_srie = {
        'problema_principal': politica.problema or '',
        'propuesta': f"{politica.titulo}: {politica.resumen_ejecutivo}",
        'contexto_ciudadano': pregunta,
        'actores_responsables': politica.entidades_responsables or '',
        'beneficiarios': politica.poblacion_objetivo or '',
        'sectores': [politica.sector_id] if politica.sector_id else [],
    }

    resultado = clasificar(datos_srie)

    return jsonify({
        'politica_titulo': politica.titulo,
        'pregunta': pregunta,
        'respuesta': f"Según la información disponible en la ficha de la política '{politica.titulo}':\n\n"
                     f"{politica.resumen_ejecutivo}\n\n"
                     f"El motor SRIE clasifica esta consulta dentro del pilar **{resultado['pilar']['nombre']}** "
                     f"(confianza: {resultado['pilar']['confianza']}%), "
                     f"con nivel de urgencia **{resultado['urgencia']['nivel']}** "
                     f"y alcance de impacto **{resultado['impacto']['nivel']}**.",
        'srie': resultado,
    })
