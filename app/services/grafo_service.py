"""Servicio del grafo de conocimiento derivado de transcripciones de grupos focales.

Convierte el texto de una sesión en nodos (chunks + temas) y aristas
(secuencia, similitud semántica, tema compartido) almacenados en la DB.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any


from app import db
from app.models.grafo import NodoGrafo, RelacionGrafo, TranscriptFocal
from app.services import llm_client

CHUNK_PALABRAS: int = 140
MAX_VECINOS: int = 5
UMBRAL_SIMILITUD: float = 0.30


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------

def chunkear_segmentos(segmentos: list[Any]) -> list[dict[str, Any]]:
    """Agrupa segmentos consecutivos en chunks de ~CHUNK_PALABRAS."""
    chunks: list[dict[str, Any]] = []
    actual: list[Any] = []
    palabras = 0

    for seg in segmentos:
        palabras_seg = len(seg.texto.split())
        if actual and palabras + palabras_seg > CHUNK_PALABRAS:
            chunks.append(_build_chunk(actual))
            # solape: el último segmento entra al siguiente chunk
            actual = [actual[-1]]
            palabras = len(actual[-1].texto.split())
        actual.append(seg)
        palabras += palabras_seg

    if actual:
        chunks.append(_build_chunk(actual))

    return chunks


def _build_chunk(segmentos: list[Any]) -> dict[str, Any]:
    texto = " ".join(s.texto.strip() for s in segmentos).strip()
    palabras = texto.split()
    titulo = " ".join(palabras[:10]) + ("..." if len(palabras) > 10 else "")
    return {
        "titulo": titulo[:300],
        "texto": texto,
        "inicio": segmentos[0].inicio_seg,
        "fin": segmentos[-1].fin_seg,
        "segmento_ids": [s.id for s in segmentos],
    }


# ---------------------------------------------------------------------------
# Construcción del grafo
# ---------------------------------------------------------------------------

def construir_grafo(transcript_id: int) -> dict[str, Any]:
    """(Re)construye nodos y aristas del grafo de un transcript. Idempotente."""
    transcript = db.session.get(TranscriptFocal, transcript_id)
    if not transcript:
        return {"ok": False, "error": f"Transcript {transcript_id} no existe"}

    # Reconstrucción idempotente: primero aristas, luego nodos (integridad FK en PostgreSQL)
    from sqlalchemy import or_

    nodos_viejos = NodoGrafo.query.filter_by(transcript_id=transcript_id).all()
    ids_viejos = [n.id for n in nodos_viejos]
    if ids_viejos:
        RelacionGrafo.query.filter(
            or_(
                RelacionGrafo.nodo_origen_id.in_(ids_viejos),
                RelacionGrafo.nodo_destino_id.in_(ids_viejos),
            )
        ).delete(synchronize_session=False)
        for nodo_viejo in nodos_viejos:
            db.session.delete(nodo_viejo)
    db.session.flush()

    segmentos = sorted(transcript.segmentos, key=lambda s: s.inicio_seg)
    if not segmentos:
        return {"ok": False, "error": "El transcript no tiene segmentos"}

    texto_completo = transcript.texto_completo
    temas = llm_client.extraer_temas(texto_completo, max_temas=5)

    chunks = chunkear_segmentos(segmentos)
    vectores = llm_client.hacer_embeddings([c["texto"] for c in chunks])

    nodos: list[NodoGrafo] = []
    for chunk, vector in zip(chunks, vectores):
        nodo = NodoGrafo(
            transcript_id=transcript_id,
            sesion_id=transcript.sesion_id,
            tipo="segmento",
            titulo=chunk["titulo"],
            texto=chunk["texto"],
            keywords=json.dumps(llm_client.keywords_fallback(chunk["texto"]), ensure_ascii=False),
            embedding=json.dumps(vector),
            metadatos=json.dumps({
                "inicio_seg": chunk["inicio"],
                "fin_seg": chunk["fin"],
                "segmento_ids": chunk["segmento_ids"],
            }, ensure_ascii=False),
            origen="transcript",
        )
        db.session.add(nodo)
        nodos.append(nodo)
    db.session.flush()

    _crear_relaciones(nodos, vectores, temas)

    db.session.commit()
    return {
        "ok": True,
        "nodos": len(nodos),
        "temas": temas or [],
        "aristas": RelacionGrafo.query.filter(
            RelacionGrafo.nodo_origen_id.in_([n.id for n in nodos])
        ).count(),
    }


def _crear_relaciones(nodos: list[NodoGrafo], vectores: list[list[float]], temas: list[str] | None) -> None:
    """Crea aristas: secuencia, similitud y tema compartido."""
    # 1. Secuencia
    for i in range(len(nodos) - 1):
        db.session.add(RelacionGrafo(
            nodo_origen_id=nodos[i].id,
            nodo_destino_id=nodos[i + 1].id,
            tipo="secuencia",
            peso=1.0,
        ))

    # 2. Similitud semántica (top-k vecinos por coseno)
    for i, vi in enumerate(vectores):
        sims = []
        for j, vj in enumerate(vectores):
            if i == j:
                continue
            peso = llm_client.coseno(vi, vj)
            if peso >= UMBRAL_SIMILITUD:
                sims.append((j, peso))
        sims.sort(key=lambda x: x[1], reverse=True)
        for j, peso in sims[:MAX_VECINOS]:
            db.session.add(RelacionGrafo(
                nodo_origen_id=nodos[i].id,
                nodo_destino_id=nodos[j].id,
                tipo="similitud",
                peso=round(peso, 4),
            ))

    # 3. Nodos de tema + aristas a segmentos relacionados
    if temas:
        for tema in temas:
            palabras_tema = set(llm_client.keywords_fallback(tema))
            if not palabras_tema:
                continue
            tema_nodo = NodoGrafo(
                transcript_id=nodos[0].transcript_id,
                sesion_id=nodos[0].sesion_id,
                tipo="tema",
                titulo=tema,
                texto=tema,
                origen="transcript",
            )
            db.session.add(tema_nodo)
            db.session.flush()
            for seg in nodos:
                seg_words = set(llm_client.keywords_fallback(seg.texto))
                if seg_words & palabras_tema:
                    db.session.add(RelacionGrafo(
                        nodo_origen_id=tema_nodo.id,
                        nodo_destino_id=seg.id,
                        tipo="tema",
                        peso=0.8,
                    ))


# ---------------------------------------------------------------------------
# Salidas para el visor
# ---------------------------------------------------------------------------

def datos_grafo(sesion_id: int) -> dict[str, Any]:
    """Nodos y aristas listos para Cytoscape.js."""
    nodos = NodoGrafo.query.filter_by(sesion_id=sesion_id).all()
    ids = {n.id for n in nodos}
    aristas = (
        RelacionGrafo.query
        .filter(RelacionGrafo.nodo_origen_id.in_(ids), RelacionGrafo.nodo_destino_id.in_(ids))
        .all()
    )

    colores = {
        "segmento": "#3B82F6",
        "tema": "#F59E0B",
        "problema": "#EF4444",
    }
    return {
        "nodos": [
            {
                "data": {
                    "id": str(n.id),
                    "label": n.titulo or n.texto[:40],
                    "tipo": n.tipo,
                    "texto": n.texto,
                    "tema": n.tema,
                    "sector": n.sector.nombre if n.sector else "",
                    "color": colores.get(n.tipo, "#94A3B8"),
                }
            }
            for n in nodos
        ],
        "aristas": [
            {
                "data": {
                    "id": f"r-{r.id}",
                    "source": str(r.nodo_origen_id),
                    "target": str(r.nodo_destino_id),
                    "tipo": r.tipo,
                    "peso": r.peso,
                }
            }
            for r in aristas
        ],
        "resumen": {"nodos": len(nodos), "aristas": len(aristas)},
    }


def exportar_html(sesion_id: int) -> str:
    """Documento HTML autónomo con el grafo (abrir en cualquier navegador)."""
    datos = datos_grafo(sesion_id)
    payload = json.dumps(datos, ensure_ascii=False)

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>Grafo — Sesión {sesion_id}</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.30.2/cytoscape.min.js"></script>
<style>
  html,body,#cy{{height:100%;margin:0;font-family:system-ui,sans-serif}}
  #bar{{position:fixed;top:0;left:0;right:0;background:#0f172a;color:#e2e8f0;padding:8px 16px;z-index:10;
       display:flex;gap:16px;align-items:center;font-size:13px}}
  #bar b{{color:#fff}}
  #cy{{margin-top:36px}}
  .leyenda{{margin-left:auto;display:flex;gap:12px;align-items:center}}
  .dot{{width:10px;height:10px;border-radius:50%;display:inline-block;margin-right:4px}}
</style>
</head>
<body>
<div id="bar">
  <b>Grafo de conocimiento — Sesión {sesion_id}</b>
  <span>{datos['resumen']['nodos']} nodos · {datos['resumen']['aristas']} aristas</span>
  <div class="leyenda">
    <span><span class="dot" style="background:#3B82F6"></span>Segmento</span>
    <span><span class="dot" style="background:#F59E0B"></span>Tema</span>
    <span><span class="dot" style="background:#EF4444"></span>Problema</span>
  </div>
</div>
<div id="cy"></div>
<script>
  const DATOS = {payload};
  const cy = cytoscape({{
    container: document.getElementById('cy'),
    elements: [...DATOS.nodos, ...DATOS.aristas],
    style: [
      {{selector:'node', style:{{
        'background-color':'data(color)',
        'label':'data(label)',
        'color':'#334155',
        'font-size':'9px',
        'text-valign':'bottom',
        'text-margin-y':'3px',
        'text-wrap':'ellipsis',
        'text-max-width':'120px',
        'width':'mapData(peso,0,1,16,40)',
        'height':'mapData(peso,0,1,16,40)'
      }}}},
      {{selector:'edge', style:{{
        'width':'mapData(peso,0,1,1,4)',
        'line-color':'#cbd5e1',
        'target-arrow-color':'#94a3b8',
        'target-arrow-shape':'triangle',
        'curve-style':'bezier',
        'opacity':'0.7'
      }}}},
      {{selector:'edge[tipo="similitud"]', style:{{'line-color':'#818cf8','opacity':'0.55'}}}},
      {{selector:'edge[tipo="tema"]', style:{{'line-color':'#f59e0b','opacity':'0.6'}}}}
    ],
    layout: {{name:'cose', animate:false, randomize:true, nodeRepulsion:5000}},
    wheelSensitivity: 0.2
  }});
  cy.on('tap', 'node', (evt) => {{
    const n = evt.target;
    alert(n.data('tipo').toUpperCase() + '\\n\\n' + (n.data('texto') || n.data('label')));
  }});
</script>
</body>
</html>"""
