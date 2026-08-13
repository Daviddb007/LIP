"""Jobs RQ de la fase "participación robusta".

Los jobs corren en el contenedor `worker` (misma imagen, proceso `python worker.py`).
La cola usa Redis (ya presente en el stack). Los audios se procesan localmente.
"""
from __future__ import annotations

import os
from typing import Any

from flask import current_app

_app = None


def get_app():
    """App Flask cacheada para el proceso worker (se crea una sola vez)."""
    global _app
    if _app is None:
        from app import create_app

        _app = create_app(os.environ.get("FLASK_CONFIG", "production"))
    return _app


# ---------------------------------------------------------------------------
# Jobs
# ---------------------------------------------------------------------------

def job_transcribir_audio(audio_id: int) -> dict[str, Any]:
    """Transcribe un audio y encola la construcción del grafo si tuvo éxito."""
    app = get_app()
    with app.app_context():
        from app import db
        from app.models.focal import AudioFocal, SesionFocal
        from app.services.transcripcion_service import procesar_audio

        resultado = procesar_audio(audio_id)

        if resultado["ok"]:
            audio = db.session.get(AudioFocal, audio_id)
            sesion = db.session.get(SesionFocal, audio.sesion_id)
            if sesion and sesion.transcript:
                try:
                    encolar_grafo(sesion.id)
                except Exception as exc:  # noqa: BLE001
                    app.logger.warning("No se pudo encolar grafo: %s", exc)

        return resultado


def job_construir_grafo(sesion_id: int) -> dict[str, Any]:
    """(Re)construye el grafo de conocimiento de una sesión transcrita."""
    app = get_app()
    with app.app_context():
        from app import db
        from app.models.focal import SesionFocal
        from app.services.grafo_service import construir_grafo

        sesion = db.session.get(SesionFocal, sesion_id)
        if not sesion or not sesion.transcript:
            return {"ok": False, "error": "La sesión no tiene transcript"}
        return construir_grafo(sesion.transcript.id)


# ---------------------------------------------------------------------------
# Encolado (desde el proceso web, dentro de app context)
# ---------------------------------------------------------------------------

def _queue(nombre: str):
    from redis import Redis
    from rq import Queue

    conn = Redis.from_url(current_app.config["RQ_CONNECTION_URI"])
    return Queue(nombre, connection=conn)


def encolar_transcripcion(audio_id: int) -> str | None:
    """Encola la transcripción de un audio. Devuelve job_id o None si Redis no está."""
    try:
        job = _queue(current_app.config["RQ_QUEUE_TRANSCRIPCION"]).enqueue(
            "app.services.worker_jobs.job_transcribir_audio",
            audio_id,
            job_timeout=7200,  # audios de hasta ~2h
        )
        return job.id
    except Exception as exc:  # noqa: BLE001 — sin Redis la transcripción queda pendiente
        current_app.logger.warning("No se pudo encolar transcripción: %s", exc)
        return None


def encolar_grafo(sesion_id: int) -> str | None:
    """Encola la construcción del grafo de una sesión."""
    try:
        job = _queue(current_app.config["RQ_QUEUE_ANALISIS"]).enqueue(
            "app.services.worker_jobs.job_construir_grafo",
            sesion_id,
            job_timeout=1800,
        )
        return job.id
    except Exception as exc:  # noqa: BLE001
        current_app.logger.warning("No se pudo encolar grafo: %s", exc)
        return None
