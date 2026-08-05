"""Mapeo contra el marco estratégico activo.

Proporciona utilidades para consultar la jerarquía del plan
y navegar entre pilares, líneas, componentes y objetivos.
"""
from __future__ import annotations

from app.models.plan import Plan, Pilar, LineaEstrategica, Componente, Objetivo


def get_plan_activo(plan_id: int = 1) -> Plan | None:
    """Retorna el plan activo por ID."""
    return Plan.query.filter_by(id=plan_id, activo=True).first()


def get_pilares_plan(plan_id: int = 1) -> list[Pilar]:
    """Retorna todos los pilares activos de un plan, ordenados."""
    return (
        Pilar.query
        .filter_by(plan_id=plan_id, activo=True)
        .order_by(Pilar.orden)
        .all()
    )


def get_lineas_pilar(pilar_id: int) -> list[LineaEstrategica]:
    """Retorna las líneas estratégicas de un pilar."""
    return (
        LineaEstrategica.query
        .filter_by(pilar_id=pilar_id)
        .order_by(LineaEstrategica.orden)
        .all()
    )


def get_componentes_linea(linea_id: int) -> list[Componente]:
    """Retorna los componentes de una línea estratégica."""
    return Componente.query.filter_by(linea_id=linea_id).all()


def get_objetivos_componente(componente_id: int) -> list[Objetivo]:
    """Retorna los objetivos de un componente."""
    return Objetivo.query.filter_by(componente_id=componente_id).all()


def get_estructura_completa(plan_id: int = 1) -> dict:
    """Retorna la estructura completa del plan como diccionario anidado.

    Útil para el Centro de Inteligencia y el dashboard público.
    """
    plan = get_plan_activo(plan_id)
    if not plan:
        return {}

    return {
        "plan": plan.to_dict(),
        "pilares": [
            {
                **pilar.to_dict(),
                "lineas": [
                    {
                        **linea.to_dict(),
                        "componentes": [
                            {
                                **comp.to_dict(),
                                "objetivos": [obj.to_dict() for obj in comp.objetivos],
                            }
                            for comp in linea.componentes
                        ],
                    }
                    for linea in pilar.lineas
                ],
            }
            for pilar in plan.pilares
        ],
    }
