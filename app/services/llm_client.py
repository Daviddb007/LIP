"""Cliente LLM configurable (gemini | openai | ninguno).

Principios de la fase "participación robusta":
  - Solo se envía TEXTO a la nube (los audios jamás salen del servidor).
  - Si el proveedor no está configurado o falla, el sistema degrada con
    elegancia usando heurísticas locales (keywords y hashing-embedding).
"""
from __future__ import annotations

import hashlib
import math
import re
import unicodedata
from typing import Any

from flask import current_app

_STOPWORDS = {
    "a", "al", "ante", "bajo", "con", "contra", "de", "del", "desde",
    "en", "entre", "hacia", "hasta", "mediante", "para", "por", "que",
    "según", "sin", "sobre", "tras", "y", "o", "u", "la", "las", "los",
    "el", "un", "una", "unos", "unas", "es", "son", "fue", "era", "ser",
    "está", "están", "estamos", "estoy", "muy", "más", "mas", "ya", "también",
    "no", "si", "se", "me", "te", "nos", "le", "les", "lo", "ello", "todo",
    "toda", "todos", "todas", "pero", "pues", "como", "cuando", "donde",
    "este", "esta", "esto", "ese", "esa", "eso", "aquí", "allí", "así",
    "tiene", "tienen", "tener", "hacer", "hace", "porque", "cuál", "cual",
    "qué", "quién", "quien", "algo", "alguien", "nada", "nadie", "uno", "algunos",
    "las", "su", "sus", "mi", "mis", "tu", "nuestro", "nuestra", "también",
}


def configurado() -> bool:
    """True si hay un proveedor LLM con API key configurado."""
    provider = current_app.config.get("LLM_PROVIDER", "ninguno").lower()
    api_key = current_app.config.get("LLM_API_KEY", "")
    return provider in ("gemini", "openai") and bool(api_key)


def proveedor() -> str:
    return current_app.config.get("LLM_PROVIDER", "ninguno").lower()


# ---------------------------------------------------------------------------
# Generación de texto (resúmenes, temas)
# ---------------------------------------------------------------------------

def resumen_sesion(texto: str, titulo: str = "") -> str | None:
    """Resumen ejecutivo de una sesión (~180 palabras). None si no hay LLM."""
    if not configurado():
        return None
    try:
        if proveedor() == "openai":
            import openai

            client = openai.OpenAI(api_key=current_app.config.get("LLM_API_KEY"))
            model = current_app.config.get("LLM_MODEL") or "gpt-4o-mini"
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "Eres un analista de política pública colombiana. "
                                                  "Genera un resumen ejecutivo de 180 palabras máximo."},
                    {"role": "user", "content": f"Sesión: {titulo}\n\n{texto[:12000]}"},
                ],
                temperature=0.3,
            )
            return resp.choices[0].message.content.strip()
        if proveedor() == "gemini":
            import google.generativeai as genai

            genai.configure(api_key=current_app.config.get("LLM_API_KEY"))
            model = genai.GenerativeModel(current_app.config.get("LLM_MODEL") or "gemini-1.5-flash")
            resp = model.generate_content(
                f"Eres un analista de política pública colombiana. Genera un resumen "
                f"ejecutivo de 180 palabras máximo.\n\nSesión: {titulo}\n\n{texto[:12000]}"
            )
            return resp.text.strip()
    except Exception as exc:  # noqa: BLE001 — degradación controlada
        current_app.logger.warning("LLM resumen falló: %s", exc)
    return None


def extraer_temas(texto: str, max_temas: int = 5) -> list[str] | None:
    """Temas principales de un texto (LLM) o keywords locales como fallback."""
    if configurado():
        temas = _temas_llm(texto)
        if temas:
            return temas
    return keywords_fallback(texto, max_temas)


def _temas_llm(texto: str, max_temas: int = 5) -> list[str] | None:
    try:
        prompt = (
            "Identifica los 5 temas principales del siguiente texto de un grupo focal "
            "sobre política pública. Responde SOLO con la lista separada por punto y coma.\n\n"
            f"{texto[:8000]}"
        )
        if proveedor() == "openai":
            import openai

            client = openai.OpenAI(api_key=current_app.config.get("LLM_API_KEY"))
            model = current_app.config.get("LLM_MODEL") or "gpt-4o-mini"
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
            )
            raw = resp.choices[0].message.content or ""
        else:
            import google.generativeai as genai

            genai.configure(api_key=current_app.config.get("LLM_API_KEY"))
            model = genai.GenerativeModel(current_app.config.get("LLM_MODEL") or "gemini-1.5-flash")
            raw = model.generate_content(prompt).text or ""
        return [t.strip() for t in raw.replace("\n", ";").split(";") if t.strip()][:max_temas]
    except Exception as exc:  # noqa: BLE001
        current_app.logger.warning("LLM temas falló: %s", exc)
    return None


# ---------------------------------------------------------------------------
# Embeddings (para similitud entre nodos)
# ---------------------------------------------------------------------------

def embed_textos(textos: list[str]) -> list[list[float]] | None:
    """Vectores de embedding para una lista de textos (None si falla)."""
    if not configurado():
        return None
    try:
        if proveedor() == "openai":
            import openai

            client = openai.OpenAI(api_key=current_app.config.get("LLM_API_KEY"))
            model = current_app.config.get("LLM_EMBEDDING_MODEL") or "text-embedding-3-small"
            resp = client.embeddings.create(model=model, input=[t[:8000] for t in textos])
            return [d.embedding for d in resp.data]
        if proveedor() == "gemini":
            import google.generativeai as genai

            genai.configure(api_key=current_app.config.get("LLM_API_KEY"))
            model = current_app.config.get("LLM_EMBEDDING_MODEL") or "models/embedding-001"
            return [
                genai.embed_content(model=model, content=t[:8000])["embedding"]
                for t in textos
            ]
    except Exception as exc:  # noqa: BLE001
        current_app.logger.warning("LLM embeddings falló: %s", exc)
    return None


def embed_texto(texto: str) -> list[float] | None:
    vectores = embed_textos([texto])
    if vectores:
        return vectores[0]
    return None


# ---------------------------------------------------------------------------
# Fallback local: keywords y hashing-embedding (sin dependencias ML)
# ---------------------------------------------------------------------------

def _normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto.lower())
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")


def keywords_fallback(texto: str, n: int = 6) -> list[str]:
    """Keywords por frecuencia de términos (stopwords en español)."""
    tokens = re.findall(r"[a-zñáéíóúü]{3,}", _normalizar(texto))
    freqs: dict[str, int] = {}
    for t in tokens:
        if t not in _STOPWORDS and len(t) >= 3:
            freqs[t] = freqs.get(t, 0) + 1
    return [t for t, _ in sorted(freqs.items(), key=lambda x: x[1], reverse=True)[:n]]


def embed_texto_fallback(texto: str, dim: int = 256) -> list[float]:
    """Vector disperso tipo hashing (sign-hashing + TF). Sin dependencias."""
    vector = [0.0] * dim
    for t in re.findall(r"[a-zñáéíóúü]{3,}", _normalizar(texto)):
        if t in _STOPWORDS:
            continue
        digest = hashlib.md5(t.encode("utf-8")).digest()
        idx = int.from_bytes(digest[:4], "big") % dim
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vector[idx] += sign
    norma = math.sqrt(sum(v * v for v in vector))
    if norma > 0:
        vector = [v / norma for v in vector]
    return vector


def coseno(a: list[float], b: list[float]) -> float:
    """Similitud coseno entre dos vectores de igual dimensión (0..1)."""
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norma_a = math.sqrt(sum(x * x for x in a))
    norma_b = math.sqrt(sum(y * y for y in b))
    if norma_a == 0.0 or norma_b == 0.0:
        return 0.0
    return dot / (norma_a * norma_b)


def hacer_embeddings(textos: list[str]) -> list[list[float]]:
    """Embeddings LLM si hay proveedor; hashing-fallback local en otro caso."""
    vectores = embed_textos(textos)
    if vectores:
        return vectores
    return [embed_texto_fallback(t) for t in textos]
