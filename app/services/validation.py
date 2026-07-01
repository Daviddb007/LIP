from app.errors import ValidationError

DEPARTAMENTOS_COL: list[str] = [
    'Amazonas', 'Antioquia', 'Arauca', 'Atlántico', 'Bolívar', 'Boyacá',
    'Caldas', 'Caquetá', 'Casanare', 'Cauca', 'Cesar', 'Chocó',
    'Córdoba', 'Cundinamarca', 'Guainía', 'Guaviare', 'Huila',
    'La Guajira', 'Magdalena', 'Meta', 'Nariño', 'Norte de Santander',
    'Putumayo', 'Quindío', 'Risaralda', 'Santander', 'Sucre', 'Tolima',
    'Valle del Cauca', 'Vaupés', 'Vichada', 'Bogotá D.C.',
]

VALID_RANGOS_EDAD: list[str] = [
    '16-18', '19-25', '26-35', '36-45', '46-55', '56-65', '66+',
]

VALID_GENEROS: list[str] = [
    'Masculino', 'Femenino', 'Otro', 'Prefiero no decir',
]


def validate_participacion(data: dict) -> None:
    """Validate participation input data. Raises ValidationError on failure."""

    _validate_sectores(data)
    _validate_propuesta(data)
    _validate_optional_fields(data)


def _validate_sectores(data: dict) -> None:
    sectores_ids = data.get('sectores', [])

    if not sectores_ids or not isinstance(sectores_ids, list):
        raise ValidationError('Debe seleccionar al menos un sector')
    if len(sectores_ids) > 3:
        raise ValidationError('Debe seleccionar máximo 3 sectores')
    if not all(isinstance(s, int) for s in sectores_ids):
        raise ValidationError('IDs de sector inválidos')


def _validate_propuesta(data: dict) -> None:
    propuesta = data.get('propuesta', '')

    if not propuesta or not propuesta.strip():
        raise ValidationError('La propuesta es requerida')
    if len(propuesta) > 500:
        raise ValidationError('La propuesta debe tener máximo 500 caracteres')


def _validate_optional_fields(data: dict) -> None:
    departamento = data.get('departamento', '')
    if departamento and departamento not in DEPARTAMENTOS_COL:
        raise ValidationError('Departamento inválido')

    rango_edad = data.get('rango_edad', '')
    if rango_edad and rango_edad not in VALID_RANGOS_EDAD:
        raise ValidationError('Rango de edad inválido')

    genero = data.get('genero', '')
    if genero and genero not in VALID_GENEROS:
        raise ValidationError('Género inválido')
