"""
Validación y sanitización de inputs para participaciones v2.

Valida los nuevos campos: problemas (M:N, 1-3), actores, beneficiarios.
Sanitiza textos libres para prevenir XSS.
"""
from __future__ import annotations

import bleach

from app.errors import ValidationError
from app.models.catalog import ProblemaCatalogo, Actor, Beneficiario, Sector

ALLOWED_TAGS: list[str] = []
ALLOWED_ATTRIBUTES: dict = {}


DEPARTAMENTOS_COL: list[str] = [
    "Amazonas", "Antioquia", "Arauca", "Atlántico", "Bogotá D.C.",
    "Bolívar", "Boyacá", "Caldas", "Caquetá", "Casanare", "Cauca",
    "Cesar", "Chocó", "Córdoba", "Cundinamarca", "Guainía", "Guaviare",
    "Huila", "La Guajira", "Magdalena", "Meta", "Nariño",
    "Norte de Santander", "Putumayo", "Quindío", "Risaralda",
    "San Andrés y Providencia", "Santander", "Sucre", "Tolima",
    "Valle del Cauca", "Vaupés", "Vichada",
]

VALID_RANGOS_EDAD: list[str] = [
    "16-18", "19-25", "26-35", "36-45", "46-55", "56-65", "66+",
]

VALID_GENEROS: list[str] = [
    "Masculino", "Femenino", "Otro", "Prefiero no decir",
]

VALID_ZONAS: list[str] = ["urbana", "rural"]


def sanitize_text(text: str) -> str:
    """Sanitiza texto libre eliminando HTML y scripts."""
    return bleach.clean(text, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES).strip()


def validate_participacion(data: dict) -> dict:
    """Valida y sanitiza datos de participación v2. Retorna datos sanitizados."""
    _validate_ubicacion(data)
    _validate_sectores(data)
    _validate_problemas(data)
    _validate_textos(data)
    _validate_gobernanza(data)

    return {
        "departamento": data["departamento"],
        "municipio": sanitize_text(data["municipio"]),
        "zona": data["zona"],
        "problema_ids": data["problema_ids"],
        "justificacion": sanitize_text(data["justificacion"]),
        "propuesta": sanitize_text(data["propuesta"]),
        "rango_edad": data.get("rango_edad"),
        "genero": data.get("genero"),
        "actor_ids": data.get("actor_ids", []),
        "beneficiario_ids": data.get("beneficiario_ids", []),
    }


def _validate_ubicacion(data: dict) -> None:
    departamento = data.get("departamento", "")
    if not departamento:
        raise ValidationError("El departamento es requerido")
    if departamento not in DEPARTAMENTOS_COL:
        raise ValidationError("Departamento inválido")

    municipio = data.get("municipio", "")
    if not municipio or not municipio.strip():
        raise ValidationError("El municipio es requerido")
    if len(municipio) > 100:
        raise ValidationError("El municipio debe tener máximo 100 caracteres")

    zona = data.get("zona", "")
    if not zona:
        raise ValidationError("La zona es requerida")
    if zona not in VALID_ZONAS:
        raise ValidationError("Zona inválida (debe ser 'urbana' o 'rural')")


def _validate_sectores(data: dict) -> None:
    """Valida que se seleccionen 1-3 sectores (compatibilidad con V2)."""
    sectores_ids = data.get('sectores', [])

    if not sectores_ids or not isinstance(sectores_ids, list):
        raise ValidationError('Debe seleccionar al menos un sector')
    if len(sectores_ids) > 3:
        raise ValidationError('Debe seleccionar máximo 3 sectores')
    if not all(isinstance(s, int) for s in sectores_ids):
        raise ValidationError('IDs de sector inválidos')


def _validate_problemas(data: dict) -> None:
    """Valida que se seleccionen 1-3 problemas del catálogo."""
    problema_ids = data.get("problema_ids")
    if not problema_ids or not isinstance(problema_ids, list):
        raise ValidationError("Debe seleccionar al menos un problema")

    if len(problema_ids) < 1:
        raise ValidationError("Debe seleccionar al menos un problema")

    if len(problema_ids) > 3:
        raise ValidationError("Puede seleccionar máximo 3 problemas")

    # Verificar que los IDs existan y estén activos
    ids = [int(pid) for pid in problema_ids]
    count = ProblemaCatalogo.query.filter(
        ProblemaCatalogo.id.in_(ids),
        ProblemaCatalogo.activo == True,
    ).count()
    if count != len(ids):
        raise ValidationError("Uno o más problemas seleccionados no son válidos")


def _validate_textos(data: dict) -> None:
    justificacion = data.get("justificacion", "")
    if not justificacion or not justificacion.strip():
        raise ValidationError("La justificación es requerida")
    if len(justificacion) > 500:
        raise ValidationError("La justificación debe tener máximo 500 caracteres")

    propuesta = data.get("propuesta", "")
    if not propuesta or not propuesta.strip():
        raise ValidationError("La propuesta es requerida")
    if len(propuesta) > 500:
        raise ValidationError("La propuesta debe tener máximo 500 caracteres")


def _validate_gobernanza(data: dict) -> None:
    """Valida actores (1-3) y beneficiarios (1-5)."""
    actor_ids = data.get("actor_ids", [])
    if not actor_ids or not isinstance(actor_ids, list):
        raise ValidationError("Debe seleccionar al menos un actor")

    if len(actor_ids) > 3:
        raise ValidationError("Puede seleccionar máximo 3 actores")

    if actor_ids:
        ids = [int(aid) for aid in actor_ids]
        count = Actor.query.filter(Actor.id.in_(ids), Actor.activo == True).count()
        if count != len(ids):
            raise ValidationError("Uno o más actores seleccionados no son válidos")

    beneficiario_ids = data.get("beneficiario_ids", [])
    if not beneficiario_ids or not isinstance(beneficiario_ids, list):
        raise ValidationError("Debe seleccionar al menos un beneficiario")

    if len(beneficiario_ids) > 5:
        raise ValidationError("Puede seleccionar máximo 5 beneficiarios")

    if beneficiario_ids:
        ids = [int(bid) for bid in beneficiario_ids]
        count = Beneficiario.query.filter(
            Beneficiario.id.in_(ids), Beneficiario.activo == True
        ).count()
        if count != len(ids):
            raise ValidationError("Uno o más beneficiarios seleccionados no son válidos")
