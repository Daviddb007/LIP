# AUDITORÍA POR BENCHMARKS — NUEVO LIP (ronda completa)

> Revisión contra benchmarks de diseño (pre-flight), accesibilidad AA, performance,
> SEO/GEO y **lo que no se estaba midiendo**. Fecha: 2026-09-28.

## 1. Lo que pasó la auditoría (OK)

- **Contraste AA/AAA:** paleta navy/gold/cream supera AA en todo texto (gold/navy 6.8:1,
  cream/navy 15.5:1, dim efectivo 6.5:1, blanco 18.6:1).
- **Sandbox funcional:** 33/33 features OK (participar POST 201, SECOP API 1.286,
  biblioteca preguntar, leads, admin, APIs, presentación, SEO).
- **Suite:** 305 tests · ruff 0.
- **Hora local:** America/Bogota aplicada (corte SECOP correcto).

## 2. Hallazgos corregidos en esta ronda

| # | Benchmark | Hallazgo | Fix |
|---|---|---|---|
| 1 | Medición | **Sin GA4** en ninguna página (no se está midiendo tráfico/eventos) | Tag GA4 en `base.html` gated por `GA4_ID` (env); se activa poniendo el ID en `.env` de producción |
| 2 | SEO técnico | **Sin canonical** en ninguna página | `<link rel="canonical" href="{{ request.base_url }}">` en base.html |
| 3 | SEO on-page | **Metas largas**: home(177), secop(181), licitar(t72/d199), consultoria(t78/d181), conocer(161) | Recortadas a title≤65 / desc≤160 |
| 4 | Schema | JSON-LD solo en secop/licitar | + `WebSite`/`Organization` en home, `ProfessionalService` en consultoria |
| 5 | GEO | llms.txt sin consultoria/presentación | Añadidos |
| 6 | Performance | **Google Fonts CDN externo** (Space Grotesk + Cormorant) = render-blocking | **Autohosteadas** (woff2 latin, ~97KB) en `fonts.css` + preload; sin Google Fonts externo |
| 7 | Diseño/CX | **CTA duplicada** ("Participa ahora" en hero y final) | Final → "Solicitar diagnóstico" (consulta); hero con 1 primaria + 1 secundaria |
| 8 | UX | Hero con 3 CTAs (sobre benchmark máx 1+1) | Reducido a 2 CTAs (presentación queda en nav/footer) |
| 9 | UX | **404 básico** | 404 premium navy/gold con CTA |

## 3. Notas / no corregido (deliberado o requiere acción del operador)

- **Eyebrows por sección** (> benchmark de 1/3 en home/iniciativa/conocer): es lenguaje de
  marca (kicker/labels semánticos que ayudan a escanear). Se mantiene; opcional reducir.
- **GA4 activo**: requiere que el operador ponga `GA4_ID` en el `.env` del hub (no se
  inventa el ID). Una vez puesto, medir con `ga4-analytics` (GA4 Data API).
- **GSC / Core Web Vitals de campo**: pendientes de setup (Search Console) y datos de
  campo reales una vez GA4/GSC activos.
- **Video hero (LCP)**: 815KB mp4 — preload="auto" + poster; aceptable, opcional versión
  recortada para LCP.

## 4. Próximas mediciones sugeridas

1. GA4 (tráfico + `lead_creado` en secop/licitar y consultoria + `participacion` en participar).
2. GSC (impresiones/clics/posición + indexación del nuevo sitemap).
3. Lighthouse en producción una vez GA4/GSC.
4. Monitoreo de corte SECOP y frescura de datos (alertas).
