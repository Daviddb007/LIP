# 🐛 Bug Tracker — Laboratorio de Inteligencia Pública (LIP)

*Generado: 2026-08-05*

## Hallazgos activos

| ID | Área | Severidad | Ruta afectada | Título | Estado |
|----|------|-----------|---------------|--------|--------|
| H-01 | Migración | ALTO | V3/ (directorio eliminado) | Migración V2→V3 con 227 archivos sin commitear | abierto |
| H-02 | Gobernanza | ALTO | app/errors.py (fan_in=6) | Hub crítico sin PIN ni rule FUNDACIONAL | resuelto (P-09) |
| H-03 | Gobernanza | ALTO | app/decorators.py (fan_in=4) | Hub transversal sin PIN ni rule FUNDACIONAL | resuelto (P-10) |
| H-04 | Gobernanza | MEDIO | holy_projects.yaml | Gate de quality/approval bloqueado | resuelto |
| H-05 | Cobertura | MEDIO | tests/ | Ratio tests/módulos 0.141 < 0.20 (9 tests vs 64 módulos) | resuelto (17 files, 53 módulos → 0.32) |
| H-06 | Deprecación | MEDIO | app/ (14 usos) | datetime.utcnow() deprecado Python 3.14 | resuelto |
| H-07 | Auditoría | MEDIO | BUGS.md, .holy/ | Sin audit trail ni SIDC; BUGS.md vacío | resuelto |
| H-08 | Refactor | BAJO | app/routes/admin.py, app/cli/migrate_v2.py | Complejidad mccabe 41 y 46 respectivamente | resuelto (2026-08-13) |
| H-09 | Despliegue | BAJO | .env.production | ADMIN_API_TOKEN missing_prod | resuelto (2026-08-13) |
| H-10 | Despliegue | ALTO | docker-compose.yml | Volumen uploads_data montado dos veces en `app` + falta RQ_CONNECTION_URI (encolado a localhost en contenedor) | resuelto |
| H-11 | Base de datos | ALTO | app/models/grafo.py, app/models/focal.py | FKs del grafo sin ondelete → IntegrityError al borrar transcript/sesión en PostgreSQL | resuelto |
| H-12 | Correctitud | ALTO | app/services/transcripcion_service.py | Reprocesar un audio transcrito duplicaba texto/segmentos en el transcript | resuelto |
| H-13 | Higiene | MEDIO | app/routes/focales.py | Archivos de audio huérfanos en disco al eliminar sesión/organización (cascade solo borra filas) | resuelto |
| H-14 | Robustez | BAJO | app/routes/focales.py | int(org_id)/int(sector_id) no validados → 500 con entrada no numérica | resuelto |
| H-15 | Correctitud | BAJO | app/services/llm_client.py | coseno() era producto punto; afectaba similitud con embeddings LLM no normalizados | resuelto |
| H-16 | Robustez | ALTO | app/routes/api_v1.py | POST /api/v1/clasificar pasaba un dict a clasificar_participacion (esperaba objeto Participacion) → 500. Corregido con clasificar_sin_persistencia() | resuelto |
| H-17 | Robustez | BAJO | app/routes/biblioteca.py | Filtro sector no numérico (int(sector_filter)) → 500 en /biblioteca y /api/politicas. Corregido con request.args.get(..., type=int) | resuelto |
| H-18 | Correctitud | MEDIO | app/templates/saas.html | JS de creación de organización apuntaba a /api/v1/organizaciones (inexistente); la ruta real es /api/organizaciones | resuelto |

## Bugs de prueba holy-core

| ID | Categoría | Severidad | Ruta afectada | Título |
|----|-----------|-----------|---------------|--------|
| LEGAL-01 | Compliance | ALTO | app/models/participacion.py | Sin columnas de consentimiento (Ley 1581) | resuelto |
| LEGAL-02 | Compliance | ALTO | app/templates/participar.html | Sin checkbox de autorización de datos | resuelto |
| LEGAL-03 | Compliance | MEDIO | base.html footer | Links legales rotos (#) sin páginas reales | resuelto |
| LEGAL-04 | Compliance | MEDIO | app/routes/ | Sin endpoints ARCO ni páginas de tratamiento de datos | resuelto |
| LEGAL-05 | Compliance | BAJO | app/templates/base.html | Sin aviso de cookies | resuelto |
| FOCAL-01 | Calidad | ALTO | app/services/grafo_service.py | Construir grafo sin segmentos debe fallar limpio (sin excepción) | resuelto |
| FOCAL-02 | Calidad | ALTO | app/routes/focales.py | Rutas de grupos focales sin login deben redirigir a autenticación | resuelto |
| FOCAL-03 | Calidad | MEDIO | app/routes/focales.py | Subida de formato de audio no permitido debe rechazarse | resuelto |
| FOCAL-04 | Calidad | ALTO | app/services/transcripcion_service.py | Reproceso de audio transcrito no debe duplicar el transcript | resuelto |

Formato de fila válida: `| ID | Categoría | Severidad | Ruta | Título |` con ID
que contenga guion (`HOLY-*`, `BUG-*`, `AUTO-*`, ...).
