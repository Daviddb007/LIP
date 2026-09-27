# PLAN — Ensamblaje del NUEVO LIP (escenario de pruebas)

> Rama de trabajo: `feat/rediseno-nuevo-lip`. Producción (master) y el catálogo
> visual quedan **intactos**. Este es el plan de alcance del nuevo LIP, mucho más
> certero, ensamblado sobre el diseño ganador **"La Escucha × VicTech"**.

---

## 1. Modelo de trabajo

| Área | Estado |
|---|---|
| **LIP producción** | Intacto (`master` → hub 204). No se toca. |
| **Catálogo visual** | Referencia fija: `~/LIP-PREMIUM-CATALOG/` (el ganador es `hibrido-4-la-escucha-victech.html`). |
| **Entorno de pruebas** | Rama `feat/rediseno-nuevo-lip` del repo LIP. Aquí se ensambla el nuevo front. |
| **Regla** | Cada paso cierra con verificación (tests verdes + render 200). Nada se despliega a producción sin GO humano (P-TRI-03). |

## 2. Diseño ganador — tokens a portar

**"La Escucha × VicTech"** (narrativa A + render VicTech + bandera):

- **Paleta:** navy `#0c1f3a` / navy-2 `#081325` + dorado `#c9a227` (único acento). Cream `#f2ead8`.
- **Tipografía:** Space Grotesk (UI/display) + Cormorant Garamond (mensajes/editorial serif) + JetBrains Mono (datos/labels).
- **Motion (GSAP):** SplitText (hero), video-scrub de la bandera, **pipeline animado** (dots que fluyen con contadores + consola de eventos), **onda de voz en canvas**, barras de telemetría que crecen, botones magnéticos, glow follower. Todo respeta `prefers-reduced-motion`.
- **Texto/mensajes:** narrativa A ("El país se construye escuchándolo", "Una política pública que no escucha es un documento…", los 3 pasos conversacionales).

## 3. Inventario de superficie actual → decisión

| Superficie actual | Rol | Decisión |
|---|---|---|
| `/participar` (wizard 5 pasos + SRIE) | **Núcleo** — participación ciudadana | **RE-DISEÑAR** (flujo + estilos + micro-copy) |
| `/resultados` + `/analitica` | Observatorio / evidencia | **UNIFICAR** en un solo "Observatorio" re-diseñado (mapa + tendencias + series) |
| `/secop` + `/secop/licitar` | Contratación pública + servicio | **RE-DISEÑAR** (mantener datos y pipeline SECOP) |
| `/biblioteca` + `/biblioteca/<id>` | Políticas públicas | **RE-DISEÑAR** |
| `/conocer` | Cómo funciona el Estado | **RE-DISEÑAR** (mantener contenido) |
| `/asistente` | Asistente SRIE | **RE-DISEÑAR** (mantener API) |
| `/iniciativa`, `/nosotros` | Institucional | **RE-DISEÑAR** (fundir en un solo bloque institucional) |
| `/armonizacion`, `/laboratorio` | Analítica avanzada | **DIFERIR** (no son core del lanzamiento) |
| `/saas/*` | Multi-tenant (línea producto) | **CORTAR del front** (dejar la API interna si aplica) |
| `/focales`, `/integraciones` | Herramientas internas | **DIFERIR** (se mantienen en backend, sin rediseño) |
| `/admin/*` | Back office | **RE-ESTILO LIGERO** (navy/gold, no rediseño funcional) |
| `/legal/*`, `/api/docs`, sitemap/robots/llms | Compliance/SEO | **MANTENER** (ajustar solo marca) |

## 4. Arquitectura de páginas del NUEVO LIP

1. **Home** — hero bandera + "El país se construye escuchándolo" + onda de voz + telemetría + CTA participar.
2. **Participar** — wizard conversacional re-diseñado + resultado SRIE.
3. **Observatorio** — evidencia: mapa + series + tendencias (fusión resultados+analítica).
4. **Visor SECOP** — procesos abiertos (filtros + pipeline visual).
5. **Licitación** — servicio para empresas que quieren contratar con el Estado.
6. **Biblioteca** — políticas públicas navegables.
7. **Conocer** — cómo funciona el Estado, en lenguaje ciudadano.
8. **Asistente SRIE** — conversa con el Estado.
9. **Institucional** — iniciativa + equipo + contacto.
10. **Legal** — tratamiento de datos, transparencia, ARCO, privacidad.

## 5. Roadmap de ensamblaje (pasos)

- **P1 · Shell y design system** — base/nav/footer/tokens/motion global (port del ganador).
- **P2 · Home + Participar** — las dos superficies más importantes end-to-end (flujo + resultado SRIE).
- **P3 · Observatorio + SECOP + Licitación** — evidencia y contratación.
- **P4 · Biblioteca + Conocer + Asistente + Institucional + Legal** — el resto.
- **P5 · QA integral** — tests, accesibilidad AA, responsive, perf, SIDC.
- **P6 · GO humano → ensamblaje final → deploy al hub** (P-TRI-03).

## 6. Criterio de término ("listo cuando")

1. Home y Participar se ven y sienten como el ganador (render 200 + motion + accesibilidad).
2. Cada página conserva su función real (datos SRIE/SECOP/biblioteca vivos).
3. Suite de tests en verde (305 actuales + nuevos) y ruff 0.
4. Sin regresión funcional del backend; sin tocar producción.

*TRINITY · LABORATORIO DE INTELIGENCIA PÚBLICA · 2026-09-27*
