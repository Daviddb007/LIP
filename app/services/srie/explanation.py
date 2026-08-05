"""
Generación de explicaciones v2 para el ciudadano.

Explica por qué su propuesta fue clasificada en los pilares que aparecen.
"""
from __future__ import annotations


def generar_explicacion(
    pilar_nombre: str,
    confianza: float,
    keywords: list[str],
    ranking: int,
) -> str:
    """Genera una explicación legible para el ciudadano.

    Args:
        pilar_nombre: Nombre del pilar
        confianza: Nivel de confianza (0.0 - 1.0)
        keywords: Lista de keywords que dispararon el match
        ranking: Posición en el top (1, 2, 3)

    Retorna string en español.
    """
    kw_text = ""
    if keywords:
        kw_display = ", ".join(keywords[:3])
        kw_text = f" (coincidencia con: {kw_display})"

    if ranking == 1:
        if confianza >= 0.80:
            return (
                f"Tu propuesta se relaciona directamente con el pilar "
                f"\"{pilar_nombre}\"{kw_text}."
            )
        if confianza >= 0.50:
            return (
                f"Tu propuesta se relaciona con el pilar "
                f"\"{pilar_nombre}\"{kw_text}. Un moderador podría ajustar "
                f"esta clasificación."
            )
        return (
            f"Tu propuesta fue clasificada provisionalmente en el pilar "
            f"\"{pilar_nombre}\"{kw_text}. La confianza es baja."
        )
    else:
        if confianza >= 0.50:
            return (
                f"Tu propuesta también se relaciona con el pilar "
                f"\"{pilar_nombre}\"{kw_text}."
            )
        return (
            f"Se detectó una relación parcial con el pilar "
            f"\"{pilar_nombre}\"{kw_text}."
        )
