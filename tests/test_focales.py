"""Tests de la fase "Estrategia de participación robusta" (grupos focales)."""
from __future__ import annotations

import io
import uuid

import pytest

from app import db
from app.models.focal import AudioFocal, OrgFocal, ParticipanteFocal, PreguntaFocal, SesionFocal
from app.models.grafo import NodoGrafo, RelacionGrafo, SegmentoTranscript, TranscriptFocal
from app.services import grafo_service, llm_client


# ---------------------------------------------------------------------------
# Fallback local del LLM (sin proveedor configurado)
# ---------------------------------------------------------------------------

def test_keywords_fallback_filtra_stopwords():
    texto = "el problema de la educación rural y la infraestructura en salud pública"
    kws = llm_client.keywords_fallback(texto, n=5)
    assert kws
    assert "el" not in kws
    assert "educación" in kws or "salud" in kws


def test_embedding_fallback_dimension_y_norma():
    v = llm_client.embed_texto_fallback("política pública de vivienda")
    assert len(v) == 256
    norma = sum(x * x for x in v) ** 0.5
    assert abs(norma - 1.0) < 1e-6


def test_coseno_textos_similares():
    a = llm_client.embed_texto_fallback("acceso a agua potable en zonas rurales")
    b = llm_client.embed_texto_fallback("agua potable acceso comunidades rurales")
    c = llm_client.embed_texto_fallback("economía digital y emprendimiento tecnológico")
    assert llm_client.coseno(a, b) > llm_client.coseno(a, c)


def test_hacer_embeddings_sin_llm_usa_fallback(app):
    with app.app_context():
        vectores = llm_client.hacer_embeddings(["texto uno", "texto dos"])
        assert len(vectores) == 2
        assert all(len(v) == 256 for v in vectores)


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------

class _SegFake:
    def __init__(self, id, inicio, fin, texto):
        self.id = id
        self.inicio_seg = inicio
        self.fin_seg = fin
        self.texto = texto


def test_chunkear_segmentos_agrupa_por_palabras():
    segmentos = []
    for i in range(10):
        segmentos.append(_SegFake(i, i * 10, i * 10 + 9, " ".join(["palabra"] * 40)))
    chunks = grafo_service.chunkear_segmentos(segmentos)
    assert len(chunks) >= 2
    for c in chunks:
        assert 0 < len(c["texto"].split()) <= grafo_service.CHUNK_PALABRAS + 40
        assert c["titulo"]
        assert "inicio" in c and "fin" in c


def test_coseno_entre_0_y_1():
    v = llm_client.embed_texto_fallback("vivienda digna en zonas rurales")
    assert abs(llm_client.coseno(v, v) - 1.0) < 1e-9
    otro = llm_client.embed_texto_fallback("economía digital")
    assert 0.0 <= llm_client.coseno(v, otro) <= 1.0
    assert llm_client.coseno([], []) == 0.0


def test_templates_focales_formularios_tienen_csrf():
    import pathlib

    raiz = pathlib.Path(__file__).resolve().parent.parent / "app" / "templates" / "admin" / "focales"
    con_formularios = ["organizacion_form.html", "sesion_form.html"]
    for nombre in con_formularios:
        contenido = (raiz / nombre).read_text(encoding="utf-8")
        assert "csrf_token" in contenido, f"{nombre} sin token CSRF"


# ---------------------------------------------------------------------------
# Rutas protegidas
# ---------------------------------------------------------------------------

def test_rutas_focales_requieren_login(client):
    for ruta in [
        "/admin/focales/organizaciones",
        "/admin/focales/sesiones",
        "/admin/focales/sesiones/nueva",
        "/admin/focales/sesiones/nueva?org_id=1",
    ]:
        r = client.get(ruta)
        assert r.status_code in (301, 302)


# ---------------------------------------------------------------------------
# Flujo completo: org → sesión → participante → pregunta → audio → grafo
# ---------------------------------------------------------------------------

@pytest.fixture()
def org(db):
    org = OrgFocal(nombre=f"Gremio Transportadores Test {uuid.uuid4().hex[:8]}", tipo="gremio", descripcion="test")
    db.session.add(org)
    db.session.commit()
    return org


def test_crear_organizacion_via_form(logged_in_client, db):
    nombre_org = f"Universidad del Test {uuid.uuid4().hex[:8]}"
    r = logged_in_client.post("/admin/focales/organizaciones/nueva", data={
        "nombre": nombre_org,
        "tipo": "universidad",
        "sector_id": "",
        "descripcion": "Prueba",
    }, follow_redirects=True)
    assert r.status_code == 200
    assert OrgFocal.query.filter_by(nombre=nombre_org).first() is not None


def test_crear_sesion(logged_in_client, db, org):
    r = logged_in_client.post("/admin/focales/sesiones/nueva", data={
        "org_id": str(org.id),
        "titulo": "Sesión sobre infraestructura",
        "fecha": "2026-08-13",
        "modalidad": "virtual",
        "lugar": "Zoom",
        "objetivo": "Escuchar al gremio",
        "estado": "programada",
    }, follow_redirects=True)
    assert r.status_code == 200
    sesion = SesionFocal.query.filter_by(org_id=org.id).first()
    assert sesion is not None
    assert sesion.titulo == "Sesión sobre infraestructura"


def test_participante_con_consentimiento(logged_in_client, db, org):
    sesion = SesionFocal(org_id=org.id, titulo="S", fecha=db.session, estado="programada")
    sesion.fecha = __import__("datetime").date(2026, 8, 13)
    db.session.add(sesion)
    db.session.commit()

    logged_in_client.post(f"/admin/focales/sesiones/{sesion.id}/participantes", data={
        "nombre": "Juan Pérez",
        "cargo": "Director",
        "consentimiento_1581": "on",
    }, follow_redirects=True)

    p = ParticipanteFocal.query.filter_by(sesion_id=sesion.id).first()
    assert p is not None
    assert p.consentimiento_aceptado is True
    assert p.consentimiento_version


def test_pregunta_categoria_presupuesto(logged_in_client, db, org):
    sesion = SesionFocal(org_id=org.id, titulo="S", fecha=__import__("datetime").date(2026, 8, 13))
    db.session.add(sesion)
    db.session.commit()

    logged_in_client.post(f"/admin/focales/sesiones/{sesion.id}/preguntas", data={
        "categoria": "presupuesto",
        "texto": "¿El presupuesto asignado refleja el valor que su sector percibe?",
    }, follow_redirects=True)

    q = PreguntaFocal.query.filter_by(sesion_id=sesion.id).first()
    assert q is not None
    assert q.categoria == "presupuesto"


def test_subir_audio(logged_in_client, db, org):
    sesion = SesionFocal(org_id=org.id, titulo="S", fecha=__import__("datetime").date(2026, 8, 13))
    db.session.add(sesion)
    db.session.commit()

    contenido = b"\x00\x01\x02RIFFfakerecord" * 1000
    r = logged_in_client.post(
        f"/admin/focales/sesiones/{sesion.id}/audios",
        data={"archivo": (io.BytesIO(contenido), "grabacion.wav")},
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert r.status_code == 200
    audio = AudioFocal.query.filter_by(sesion_id=sesion.id).first()
    assert audio is not None
    assert audio.formato == "wav"
    assert len(audio.sha256) == 64
    assert audio.estado in ("pendiente", "en_cola")


def test_descarga_audio_autenticada(logged_in_client, db, org):
    import os

    sesion = SesionFocal(org_id=org.id, titulo="S", fecha=__import__("datetime").date(2026, 8, 13))
    db.session.add(sesion)
    db.session.commit()

    from flask import current_app

    directorio = os.path.join(current_app.config["UPLOADS_DIR"], f"sesion_{sesion.id}")
    os.makedirs(directorio, exist_ok=True)
    ruta = os.path.join(directorio, "prueba.wav")
    with open(ruta, "wb") as f:
        f.write(b"datos")
    audio = AudioFocal(
        sesion_id=sesion.id,
        nombre_original="prueba.wav",
        ruta_archivo=os.path.abspath(ruta),
        tamano_bytes=5,
        formato="wav",
        sha256="a" * 64,
        estado="pendiente",
    )
    db.session.add(audio)
    db.session.commit()

    r = logged_in_client.get(f"/admin/focales/audios/{audio.id}/descargar")
    assert r.status_code == 200
    assert r.data == b"datos"


def test_no_subir_formato_invalido(logged_in_client, db, org):
    sesion = SesionFocal(org_id=org.id, titulo="S", fecha=__import__("datetime").date(2026, 8, 13))
    db.session.add(sesion)
    db.session.commit()
    r = logged_in_client.post(
        f"/admin/focales/sesiones/{sesion.id}/audios",
        data={"archivo": (io.BytesIO(b"x" * 10), "documento.exe")},
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert AudioFocal.query.filter_by(sesion_id=sesion.id).first() is None


def test_reprocesar_audio_transcrito_no_duplica(db, org):
    from app.services.transcripcion_service import procesar_audio

    sesion = SesionFocal(org_id=org.id, titulo="S", fecha=__import__("datetime").date(2026, 8, 13))
    db.session.add(sesion)
    db.session.flush()
    transcript = TranscriptFocal(sesion_id=sesion.id, texto_completo="texto original")
    db.session.add(transcript)
    db.session.flush()
    audio = AudioFocal(
        sesion_id=sesion.id,
        nombre_original="a.wav",
        ruta_archivo="/tmp/a.wav",
        tamano_bytes=1,
        formato="wav",
        sha256="b" * 64,
        estado="transcrito",
        transcript_id=transcript.id,
    )
    db.session.add(audio)
    db.session.commit()

    resultado = procesar_audio(audio.id)
    assert resultado["ya_transcrito"] is True
    db.session.refresh(transcript)
    assert transcript.texto_completo == "texto original"
    assert transcript.segmentos == []
    assert audio.estado == "transcrito"


def test_reprocesar_ruta_rechaza_transcrito(logged_in_client, db, org):
    sesion = SesionFocal(org_id=org.id, titulo="S", fecha=__import__("datetime").date(2026, 8, 13))
    db.session.add(sesion)
    db.session.flush()
    transcript = TranscriptFocal(sesion_id=sesion.id, texto_completo="t")
    db.session.add(transcript)
    db.session.flush()
    audio = AudioFocal(
        sesion_id=sesion.id,
        nombre_original="a.wav",
        ruta_archivo="/tmp/a.wav",
        tamano_bytes=1,
        formato="wav",
        sha256="c" * 64,
        estado="transcrito",
        transcript_id=transcript.id,
    )
    db.session.add(audio)
    db.session.commit()

    logged_in_client.post(f"/admin/focales/audios/{audio.id}/reprocesar", follow_redirects=True)
    db.session.refresh(audio)
    assert audio.estado == "transcrito"


def test_sesion_eliminar_limpia_directorio_audios(logged_in_client, db, org):
    import os

    from flask import current_app

    sesion = SesionFocal(org_id=org.id, titulo="S", fecha=__import__("datetime").date(2026, 8, 13))
    db.session.add(sesion)
    db.session.commit()
    directorio = os.path.join(current_app.config["UPLOADS_DIR"], f"sesion_{sesion.id}")
    os.makedirs(directorio, exist_ok=True)
    with open(os.path.join(directorio, "huérfano.wav"), "wb") as f:
        f.write(b"x")

    logged_in_client.post(f"/admin/focales/sesiones/{sesion.id}/eliminar", follow_redirects=True)
    assert not os.path.exists(directorio)
    assert db.session.get(SesionFocal, sesion.id) is None


# ---------------------------------------------------------------------------
# Grafo de conocimiento
# ---------------------------------------------------------------------------

def _crear_sesion_transcrita(db, org, n_segmentos=6):
    sesion = SesionFocal(org_id=org.id, titulo="S", fecha=__import__("datetime").date(2026, 8, 13))
    db.session.add(sesion)
    db.session.flush()
    texto = " ".join(["salud educación infraestructura agua vivienda empleo"] * 40)
    transcript = TranscriptFocal(sesion_id=sesion.id, texto_completo=texto)
    db.session.add(transcript)
    db.session.flush()
    for i in range(n_segmentos):
        db.session.add(SegmentoTranscript(
            transcript_id=transcript.id,
            inicio_seg=i * 10,
            fin_seg=i * 10 + 9,
            texto=f"segmento {i}: " + " ".join(
                ["acceso a salud, educación, agua potable, infraestructura y vivienda en el territorio"] * 8
            ),
        ))
    db.session.commit()
    return sesion, transcript


def test_construir_grafo_crea_nodos_y_aristas(db, org):
    sesion, transcript = _crear_sesion_transcrita(db, org)
    resultado = grafo_service.construir_grafo(transcript.id)
    assert resultado["ok"] is True
    assert resultado["nodos"] >= 2

    nodos = NodoGrafo.query.filter_by(sesion_id=sesion.id).all()
    assert len(nodos) >= 3
    assert any(n.tipo == "tema" for n in nodos)  # temas con fallback de keywords

    aristas = RelacionGrafo.query.filter(
        (RelacionGrafo.nodo_origen_id.in_([n.id for n in nodos])) |
        (RelacionGrafo.nodo_destino_id.in_([n.id for n in nodos]))
    ).all()
    assert len(aristas) >= 1
    tipos = {a.tipo for a in aristas}
    assert "secuencia" in tipos


def test_construir_grafo_es_idempotente(db, org):
    sesion, transcript = _crear_sesion_transcrita(db, org)
    grafo_service.construir_grafo(transcript.id)
    primero = NodoGrafo.query.count()
    grafo_service.construir_grafo(transcript.id)
    segundo = NodoGrafo.query.count()
    assert primero == segundo
    assert primero > 0


def test_datos_grafo_y_export_html(db, org):
    sesion, transcript = _crear_sesion_transcrita(db, org)
    grafo_service.construir_grafo(transcript.id)

    datos = grafo_service.datos_grafo(sesion.id)
    assert datos["resumen"]["nodos"] >= 2
    assert datos["nodos"][0]["data"]["id"]

    html = grafo_service.exportar_html(sesion.id)
    assert "cytoscape" in html
    assert f"Sesión {sesion.id}" in html


def test_construir_grafo_sin_segmentos(db, org):
    sesion = SesionFocal(org_id=org.id, titulo="S", fecha=__import__("datetime").date(2026, 8, 13))
    db.session.add(sesion)
    db.session.flush()
    transcript = TranscriptFocal(sesion_id=sesion.id, texto_completo="")
    db.session.add(transcript)
    db.session.commit()
    resultado = grafo_service.construir_grafo(transcript.id)
    assert resultado["ok"] is False
