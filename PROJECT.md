# PROJECT.md — ADN técnico

> Documento de **cómo** (arquitectura/stack). Complementa a `ALCANCEGLOBAL.md`
> (por qué / hacia dónde). Todo agente lo lee antes de construir (P-ALC-01).

---

## Laboratorio de Inteligencia Pública V3 — Construyamos Colombia

### Stack

| Capa | Tecnología |
|------|-----------|
| **Backend** | Flask 3.1, SQLAlchemy 2.0 |
| **Bases de datos** | PostgreSQL 16, Redis 7 |
| **Servidor** | Gunicorn 23 + Nginx |
| **Frontend** | Jinja2, Bootstrap 5 (custom), Vanilla JS ES6, Chart.js 4 |
| **Seguridad** | CSRF, rate limiting, bleach sanitization, security headers, gzip |
| **Infraestructura** | Docker Compose, multi-stage build, health checks |

### Arquitectura / módulos

- **Motor SRIE:** clasificación automática de propuestas contra marco estratégico
  configurable: Plan → Pilar → Línea → Componente → Objetivo → Indicador.
- **Formulario conversacional:** 5 pasos + resultado inmediato (participación).
- **Dashboard público + Centro de Inteligencia:** mapa SVG, charts, tendencias, 9 módulos de admin.

### Superficie real (app/)

- **Rutas (`app/routes/`):** admin, analitica, api_v1, armonizacion, asistente,
  biblioteca, conocimiento, focales, health, home, iniciativa, integraciones,
  laboratorio, legal, nosotros, participar, resultados, saas.
- **Modelos (`app/models/`):** api_token, catalog, focal, grafo, miembro, organizacion,
  participacion, plan, politica, webhook.
- **Servicios (`app/services/`):** alertas, analitica, armonizacion, asistente,
  conocimiento, export, grafo.
- **Otros:** `app/forms.py`, `app/decorators.py`, `app/errors.py`, `app/cli/`, `app/seed/`.

### Comandos

- Deploy: `docker compose up -d` + `docker compose exec app flask seed`
- Tests: `py -m pytest tests/ -v --tb=short`

### Estándares

- Migraciones para todo cambio de esquema (P-DEP-06).
- Seguridad por capas (CSRF, sanitización, rate limiting).
- Refactor Flask al patrón de fábrica de aplicación (si toca Flask).
