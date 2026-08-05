"""
Matching semántico v2: texto → pilar del plan estratégico.

Multi-pilar scoring con keywords ponderadas y sector boost.
Retorna top-3 clasificaciones.
"""
from __future__ import annotations

import re
import unicodedata

from app.models.plan import Pilar
from app.services.srie.keywords import (
    KEYWORDS_PILARES, SECTOR_PILAR_BOOST, PROBLEMA_PILAR_SLUG_MAP,
)


def _normalize(text: str) -> str:
    """Normaliza texto: minúsculas, sin tildes, espacios múltiples."""
    text = text.lower().strip()
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"\s+", " ", text)
    return text


def _score_pilar(text: str, keywords: list[tuple[str, float]]) -> tuple[float, list[str]]:
    """Scoring de un pilar contra el texto normalizado.

    Retorna (score_acumulado, keywords_encontradas).
    """
    score = 0.0
    found = []
    text_lower = text.lower()

    for keyword, peso in keywords:
        if keyword in text_lower:
            score += peso
            found.append(keyword)

    # Normalizar score a 0-1 (cap en 5.0)
    normalized = min(score / 5.0, 1.0)
    return normalized, found


def clasificar_texto(
    texto: str,
    problema_slug: str | None = None,
    sector_slug: str | None = None,
    top_n: int = 3,
) -> list[dict]:
    """Clasifica un texto contra todos los pilares.

    Retorna lista de top-N dicts:
        {"pilar_slug": str, "score": float, "keywords": [str]}
    """
    normalized = _normalize(texto)
    scores: dict[str, tuple[float, list[str]]] = {}

    # 1. Scoring base contra keywords
    for pilar_slug, keywords in KEYWORDS_PILARES.items():
        score, kw_found = _score_pilar(normalized, keywords)
        if kw_found:
            scores[pilar_slug] = (score, kw_found)

    # 2. Sector boost: si se indica sector, bonus de +0.15 al pilar asociado
    if sector_slug and sector_slug in SECTOR_PILAR_BOOST:
        boost_pilar = SECTOR_PILAR_BOOST[sector_slug]
        if boost_pilar in scores:
            old_score, kw = scores[boost_pilar]
            scores[boost_pilar] = (min(old_score + 0.15, 1.0), kw)
        else:
            scores[boost_pilar] = (0.15, [])

    # 3. Problema directo: boost fuerte (+0.3) al pilar del problema seleccionado
    if problema_slug and problema_slug in PROBLEMA_PILAR_SLUG_MAP:
        direct_pilar = PROBLEMA_PILAR_SLUG_MAP[problema_slug]
        if direct_pilar in scores:
            old_score, kw = scores[direct_pilar]
            scores[direct_pilar] = (min(old_score + 0.3, 1.0), kw)
        else:
            scores[direct_pilar] = (0.3, [problema_slug])

    # 4. Ordenar y tomar top-N
    sorted_pilares = sorted(scores.items(), key=lambda x: x[1][0], reverse=True)

    results = []
    for pilar_slug, (score, keywords) in sorted_pilares[:top_n]:
        results.append({
            "pilar_slug": pilar_slug,
            "score": round(score, 4),
            "keywords": keywords,
        })

    # Si no hay resultados, retornar "sin clasificar"
    if not results:
        results.append({
            "pilar_slug": "pilar-democratico",
            "score": 0.0,
            "keywords": [],
        })

    return results


def get_pilar_by_slug(slug: str) -> Pilar | None:
    """Busca un pilar por slug en la BD."""
    return Pilar.query.filter_by(slug=slug, activo=True).first()
