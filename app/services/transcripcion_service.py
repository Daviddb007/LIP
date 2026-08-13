"""Servicio de transcripción local de audios de grupos focales.

Usa faster-whisper (whisper local): los audios NUNCA salen del servidor.
Cada sesión puede tener varios audios; todos se fusionan en un único
TranscriptFocal por sesión (los segmentos se anexan).
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from flask import current_app

from app import db
from app.models.focal import AudioFocal
from app.models.grafo import TranscriptFocal, SegmentoTranscript


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def transcribir_audio_local(
    ruta_archivo: str,
    modelo: str | None = None,
    device: str | None = None,
    compute_type: str | None = None,
) -> dict[str, Any]:
    """Transcribe un archivo de audio con whisper local. Devuelve texto, segmentos, idioma y duración."""
    from faster_whisper import WhisperModel

    modelo = modelo or current_app.config.get("WHISPER_MODEL", "small")
    device = device or current_app.config.get("WHISPER_DEVICE", "cpu")
    compute_type = compute_type or current_app.config.get("WHISPER_COMPUTE_TYPE", "int8")

    model = WhisperModel(modelo, device=device, compute_type=compute_type)
    segments, info = model.transcribe(ruta_archivo, beam_size=5, vad_filter=True)

    lista_segmentos: list[dict[str, Any]] = []
    for seg in segments:
        texto = (seg.text or "").strip()
        if texto:
            lista_segmentos.append({"inicio": float(seg.start), "fin": float(seg.end), "texto": texto})

    return {
        "texto": "\n".join(s["texto"] for s in lista_segmentos),
        "segmentos": lista_segmentos,
        "idioma": getattr(info, "language", None),
        "duracion": getattr(info, "duration", None),
    }


def procesar_audio(audio_id: int) -> dict[str, Any]:
    """Transcribe un AudioFocal y fusiona el resultado en el transcript de su sesión."""
    audio = db.session.get(AudioFocal, audio_id)
    if not audio:
        return {"ok": False, "error": f"AudioFocal {audio_id} no existe"}

    if audio.transcript_id is not None:
        # Ya contribuyó al transcript de su sesión: reprocesar aquí duplicaría
        # texto y segmentos. Para re-transcribir hay que reconstruir el transcript.
        return {"ok": True, "ya_transcrito": True, "transcript_id": audio.transcript_id}

    audio.estado = "procesando"
    audio.error_mensaje = None
    db.session.commit()
    current_app.logger.info("Transcribiendo audio %s (%s)", audio_id, audio.nombre_original)

    try:
        ruta = audio.ruta_archivo
        resultado = transcribir_audio_local(ruta)
        if not resultado["texto"].strip():
            raise ValueError("El audio no produjo texto (posible silencio o formato inválido).")

        sesion = audio.sesion
        transcript = sesion.transcript

        if not transcript:
            transcript = TranscriptFocal(
                sesion_id=sesion.id,
                texto_completo=resultado["texto"],
                formato="txt",
                modelo_usado=current_app.config.get("WHISPER_MODEL", "small"),
                idioma=resultado["idioma"],
                duracion_segundos=resultado["duracion"],
                procesado_por=f"audio-{audio_id}",
            )
            db.session.add(transcript)
            db.session.flush()
        else:
            transcript.texto_completo += "\n\n" + resultado["texto"]
            transcript.procesado_por += f",audio-{audio_id}"
            if resultado["idioma"] and not transcript.idioma:
                transcript.idioma = resultado["idioma"]
            if transcript.duracion_segundos:
                transcript.duracion_segundos += float(resultado["duracion"] or 0)
            else:
                transcript.duracion_segundos = resultado["duracion"]
            transcript.updated_at = _now()

        for seg in resultado["segmentos"]:
            db.session.add(SegmentoTranscript(
                transcript_id=transcript.id,
                audio_id=audio.id,
                inicio_seg=seg["inicio"],
                fin_seg=seg["fin"],
                texto=seg["texto"],
            ))

        audio.transcript_id = transcript.id
        audio.duracion_segundos = resultado["duracion"]
        audio.estado = "transcrito"
        db.session.commit()

        return {
            "ok": True,
            "transcript_id": transcript.id,
            "palabras": len(resultado["texto"].split()),
            "segmentos": len(resultado["segmentos"]),
            "idioma": resultado["idioma"],
        }
    except Exception as exc:  # noqa: BLE001 — el error queda registrado en el audio
        current_app.logger.exception("Error transcribiendo audio %s", audio_id)
        audio.estado = "error"
        audio.error_mensaje = str(exc)[:2000]
        db.session.commit()
        return {"ok": False, "error": str(exc)[:2000]}
