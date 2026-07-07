from flask import Blueprint, jsonify, request, current_app

from app import limiter
from app.models.api_token import ApiToken
from app.models.participacion import Participacion
from app.models.politica import Politica
from app.models.sector import Sector
from app.services.stats_service import get_estadisticas_completas, get_estadisticas_generales
from app.services.armonizacion_service import generar_armonizacion
from app.services.analitica_service import obtener_analitica
from app.services.srie_service import clasificar

api_v1_bp = Blueprint('api_v1', __name__, url_prefix='/api/v1')


def autenticar():
    token_str = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token_str:
        token_str = request.args.get('token', '')
    if not token_str:
        return None
    return ApiToken.verificar(token_str)


def requerir_auth(f):
    from functools import wraps
    @wraps(f)
    def decorada(*args, **kwargs):
        token = autenticar()
        if not token:
            return jsonify({'error': 'Token inválido o inactivo', 'docs': '/api/docs'}), 401
        token.last_used_at = __import__('datetime').datetime.now(__import__('datetime').timezone.utc)
        from app import db
        db.session.commit()
        return f(*args, **kwargs)
    return decorada


def requerir_role(role_minimo):
    from functools import wraps
    def decorator(f):
        @wraps(f)
        def decorada(*args, **kwargs):
            token = autenticar()
            if not token:
                return jsonify({'error': 'Token requerido', 'docs': '/api/docs'}), 401
            jerarquia = {'lectura': 1, 'escritura': 2, 'admin': 3}
            if jerarquia.get(token.role, 0) < jerarquia.get(role_minimo, 99):
                return jsonify({'error': 'Permiso insuficiente'}), 403
            return f(*args, **kwargs)
        return decorada
    return decorator


@api_v1_bp.route('/')
@limiter.limit("30 per minute")
def api_root():
    return jsonify({
        'api': 'Construyamos Colombia API v1',
        'version': '1.0.0',
        'documentacion': '/api/docs',
        'endpoints': {
            'GET /api/v1/estadisticas': 'Estadísticas generales del ecosistema',
            'GET /api/v1/participaciones': 'Listado de participaciones ciudadanas',
            'GET /api/v1/politicas': 'Listado de políticas públicas',
            'GET /api/v1/politicas/<id>': 'Detalle de una política',
            'GET /api/v1/sectores': 'Sectores activos',
            'GET /api/v1/armonizacion': 'Matriz de armonización estratégica',
            'GET /api/v1/analitica': 'Analítica avanzada del ecosistema',
            'POST /api/v1/clasificar': 'Clasificar texto con motor SRIE',
            'POST /api/v1/token': 'Generar token de acceso (admin)',
        },
    })


@api_v1_bp.route('/estadisticas')
@limiter.limit("60 per minute")
def api_estadisticas():
    return jsonify(get_estadisticas_completas())


@api_v1_bp.route('/participaciones')
@limiter.limit("30 per minute")
@requerir_auth
def api_participaciones():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 50, type=int), 100)
    sector = request.args.get('sector', '')
    departamento = request.args.get('departamento', '')

    query = Participacion.query.order_by(Participacion.created_at.desc())

    if sector:
        query = query.join(Participacion.sectores).filter(Sector.nombre == sector)
    if departamento:
        query = query.filter(Participacion.departamento == departamento)

    pagination = query.paginate(page=page, per_page=per_page)
    return jsonify({
        'data': [p.to_dict() for p in pagination.items],
        'total': pagination.total,
        'page': pagination.page,
        'pages': pagination.pages,
        'per_page': per_page,
    })


@api_v1_bp.route('/politicas')
def api_politicas():
    sector = request.args.get('sector', '')
    query = Politica.query.filter_by(activo=True)
    if sector:
        query = query.filter(Politica.sector_id == int(sector))
    politicas = query.order_by(Politica.created_at.desc()).all()
    return jsonify({
        'total': len(politicas),
        'data': [p.to_dict() for p in politicas],
    })


@api_v1_bp.route('/politicas/<int:politica_id>')
def api_politica_detalle(politica_id):
    politica = Politica.query.get_or_404(politica_id)
    return jsonify(politica.to_dict())


@api_v1_bp.route('/sectores')
def api_sectores():
    sectores = Sector.find_active()
    return jsonify({
        'total': len(sectores),
        'data': [s.to_dict() for s in sectores],
    })


@api_v1_bp.route('/armonizacion')
def api_armonizacion():
    return jsonify(generar_armonizacion())


@api_v1_bp.route('/analitica')
def api_analitica():
    return jsonify(obtener_analitica())


@api_v1_bp.route('/clasificar', methods=['POST'])
@limiter.limit("10 per minute")
def api_clasificar():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'JSON requerido'}), 400
    return jsonify(clasificar(data))


@api_v1_bp.route('/token', methods=['POST'])
@limiter.limit("5 per minute")
def api_generar_token():
    data = request.get_json(silent=True) or {}
    nombre = data.get('nombre', '').strip()
    role = data.get('role', 'lectura')

    if not nombre:
        return jsonify({'error': 'nombre requerido'}), 400

    admin_token = request.headers.get('Authorization', '').replace('Bearer ', '')
    admin_config = current_app.config.get('ADMIN_API_TOKEN', '')

    if admin_token != admin_config:
        return jsonify({'error': 'Token de administración inválido'}), 403

    api_token = ApiToken.generar(nombre, role)
    return jsonify(api_token.to_dict()), 201
