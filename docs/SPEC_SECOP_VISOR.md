# SPEC — Onda 2: Visor SECOP Público + Servicio de Licitación (Inteligencia Pública)

> Gate P-SDD-01 (spec-before-code). Aprobación humana requerida antes de implementar.
> Proyecto: LIP (Construyamos Colombia · powered by Stonelytics). Fecha: 2026-09-26.

## Objetivo de valor

Convertir a LIP en la referencia de **Inteligencia Pública** cargando datos vivos de
SECOP II (contratación pública de Colombia) en un **visor público** + un **servicio
comercial de licitación** para empresas que quieren contratar con el Estado. Esto
cierra el sello 1 (SEO/ventas), sello 5 (funcionamiento) y sello 6 (reaprovecha
`Radar_SECOP`, no se rehace).

## Reutilización (sello 6)

`Radar_SECOP` (`~/Radar_SECOP`) ya descarga/normaliza/valida procesos con oferta
abierta del dataset `p6dx-8zbt` (datos.gov.co) → **883 procesos vigentes (corte
2026-09-26)**, diccionario en `data/DATA.md`, dashboard estático. Se **porta su
lógica de descarga a Python** (CLI de Flask) y se sirve como página viva en LIP.

## 1. Datos — Ingesta SECOP II a PostgreSQL

- **Modelos nuevos** (`app/models/secop.py`):
  - `SecopProceso`: entidad, departamento, ciudad, nombre, modalidad, tipo_contrato,
    valor (BigInteger COP), requiere_rup (bool), fecha_limite (Date), corte (Date),
    temas (JSON), url (única por proceso+corte), creado_at.
  - `SecopCorte`: corte (Date, único), generado_at, total.
  - `LeadSecop`: nombre, empresa, email, teléfono, sector, mensaje, creado_at, atendido (bool).
- **Servicio** (`app/services/secop_service.py`): descarga paginada a datos.gov.co,
  filtros (fase `Presentación de oferta`, estado `Abierto`, fecha ≥ corte), normalización
  (idem `update-data.mjs`), validación estricta (campos obligatorios, valor ≥ 0, URL
  `noticeUID=` bien formada, fecha válida) → **si la data no pasa, no se publica**.
- **CLI** (`app/cli/`): `flask secop-actualizar [--corte YYYY-MM-DD]` — upsert por
  (url, corte); guarda `SecopCorte`.
- Esquema vía `db.create_all()` (patrón documentado del repo, P-DEP-06; no Alembic).

## 2. Visor público `/secop`

- Blueprint `app/routes/secop.py`:
  - `GET /secop` — dashboard renderizado en servidor: métricas (procesos vigentes,
    valor total COP, entidades, % sin RUP, próximos vencimientos), filtros
    (departamento, modalidad, requiere_rup, búsqueda texto), tabla paginada ordenada
    por fecha límite, **Chart.js** (por departamento, por modalidad, por valor).
    Meta visible: corte, fecha de actualización, nº procesos, fuente + disclaimer
    "verifica siempre en SECOP".
  - `GET /secop/api/datos` — JSON para gráficos con filtros (cache 60s).
- **Cross-ref con SRIE** (inteligencia pública): cada proceso se etiqueta con el pilar
  PND afín (salud, educación, seguridad, campo, corrupción, TI…) → el visor puede
  filtrar "procesos abiertos por pilar" y se abre la puerta a armonización con la
  participación ciudadana en ondas futuras.

## 3. Servicio comercial de licitación `/secop/licitar`

- Página pública dedicada (SEO): **"¿Tu empresa quiere empezar a licitar en lo
  público? Te ayudamos a licitar — tenemos el equipo de profesionales disponible."**
  - Propuesta de valor: cómo funciona (3 pasos), qué incluye (RUP, búsqueda de
    oportunidades en SECOP, preparación de propuestas, documentos, seguimiento),
    profesionales disponibles, doble CTA.
  - **Formulario de lead** (CSRF global + rate limit + sanitización + validación):
    nombre, empresa, email, teléfono, sector → `POST /secop/licitar/lead`.
  - Guarda `LeadSecop`; **lista mínima en admin** (`/admin/secop-leads`) para
    seguimiento comercial.

## 4. SEO / GEO (ronda completa)

- `GET /sitemap.xml` — públicas: home, iniciativa, participar, conocer, biblioteca,
  resultados, analitica, asistente, armonizacion, laboratorio, secop, secop/licitar,
  nosotros, saas (listado), legal.
- `GET /robots.txt` — permite todo + referencia al sitemap (GEO: deja pasar crawlers IA).
- `GET /llms.txt` — GEO: qué es LIP, qué es el visor SECOP, URLs clave, contacto.
- **JSON-LD**:
  - `/secop` → `Dataset` (SECOP II, fuente datos.gov.co, cobertura Colombia) + `BreadcrumbList`.
  - `/secop/licitar` → `ProfessionalService` (StoneLytics) + `FAQPage`.
- Titles ≤65 / descriptions ≤160 en las páginas nuevas; OG/Twitter.
- **GEO answer-first**: FAQ en `/secop` ("¿Qué es SECOP II?", "¿Cómo empiezo a licitar
  con el Estado?", "¿Qué es el RUP?") — contenido citable para AI Overviews/Gemini.

## 5. Navegación

- Navbar + footer: ítem **"SECOP"** → `/secop`; CTA **"Licitamos por ti"** → `/secop/licitar`.

## 6. Tests (P-QA-01)

- `tests/test_secop.py`: servicio (normalización + validación con fetch mockeado),
  rutas (`GET /secop` 200 con data, `GET /secop/licitar` 200), POST lead
  (válido/ inválido / sanitización), `sitemap.xml` incluye `/secop`, robots y llms.txt
  200. Suite total debe quedar **en verde** (287 + nuevos).

## 7. Fuera de alcance (esta onda)

- Alertas/notificaciones de oportunidades por email/WhatsApp.
- Detalle por proceso (`/secop/<id>`) y usuario.
- Armonización SECOP↔participación (se habilita la data, no la feature).
- Deploy a producción (requiere GO humano P-TRI-03).

## Criterio de término ("listo cuando")

1. `flask secop-actualizar` descarga, valida y persiste (corte 2026-09-26 o más nuevo).
2. `/secop` renderiza métricas + tabla + gráficos con datos reales (200 en vivo local).
3. `/secop/licitar` muestra la propuesta + formulario que guarda leads (admin los ve).
4. sitemap/robots/llms.txt + JSON-LD + metas implementados y verificables.
5. `ruff check` 0 y suite completa en verde.

---

## Estado de implementación (2026-09-26)

**IMPLEMENTADO Y VERIFICADO:**

- [x] Modelos `SecopProceso`, `SecopCorte`, `LeadSecop` (`app/models/secop.py`) + cross-ref pilares SRIE.
- [x] Servicio `app/services/secop_service.py` (port del pipeline Radar_SECOP: descarga paginada datos.gov.co, normalización, validación estricta, persistencia por corte).
- [x] CLI `flask secop-actualizar [--corte YYYY-MM-DD]` — **883 procesos vigentes (corte 26 sep 2026) cargados y verificados en vivo**.
- [x] Visor `/secop` (métricas, filtros q/departamento/modalidad/RUP/pilar, tabla paginada, Chart.js por departamento/modalidad/pilar, FAQ GEO, CTA licitación).
- [x] Servicio `/secop/licitar` + formulario de lead (CSRF + rate limit + sanitización bleach + email-validator) → `LeadSecop`.
- [x] Admin `/admin/secop-leads` (lista + marcar atendido).
- [x] SEO/GEO: `/sitemap.xml` (21 URLs), `/robots.txt` (permite crawlers IA + sitemap), `/llms.txt`, JSON-LD `Dataset` (/secop) y `ProfessionalService` + `FAQPage` (/secop/licitar), metas ≤65/160.
- [x] Nav/footer con enlaces SECOP + CTA licitación.
- [x] Tests `tests/test_secop.py` (18) — suite total **305 verdes · ruff 0**.

Pendiente fuera de alcance (próximas ondas): alertas/notificaciones de oportunidades, detalle por proceso, armonización SECOP↔participación, y **deploy a producción (requiere GO humano P-TRI-03)**.
