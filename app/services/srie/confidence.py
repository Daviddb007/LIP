"""
Cálculo de confianza para clasificaciones SRIE v2.

Combina score del matcher con factores contextuales (texto largo, problema seleccionado).
"""
from __future__ import annotations


def calcular_confianza(
    score: float,
    justificacion: str,
    propuesta: str,
    keywords_encontradas: list[str],
    tiene_problema_directo: bool,
) -> float:
    """Calcula la confianza final de una clasificación.

    Args:
        score: Score normalizado del matcher (0.0 - 1.0)
        justificacion: Texto de justificación del ciudadano
        propuesta: Texto de propuesta del ciudadano
        keywords_encontradas: Lista de keywords que matchearon
        tiene_problema_directo: Si el problema seleccionado tiene mapping directo al pilar

    Retorna:
        confianza entre 0.0 y 1.0
    """
    confianza = score

    # Bonus por problema directo (problema seleccionado → pilar directo)
    if tiene_problema_directo:
        confianza = min(confianza + 0.10, 1.0)

    # Bonus por texto sustancial (justificación + propuesta > 100 chars)
    texto_total = f"{justificacion} {propuesta}"
    if len(texto_total) > 200:
        confianza = min(confianza + 0.05, 1.0)
    elif len(texto_total) > 100:
        confianza = min(confianza + 0.03, 1.0)

    # Bonus por keywords fuertes (peso >= 0.9)
    # ya está implícito en el score del matcher

    # Penalización por pocas keywords (solo 1 keyword encontrada)
    if len(keywords_encontradas) == 1:
        confianza = max(confianza - 0.05, 0.0)

    return round(confianza, 2)
