# 🐛 Bug Tracker — Laboratorio de Inteligencia Pública (LIP)

*Generado: 2026-08-05*

## Hallazgos activos

| ID | Área | Severidad | Ruta afectada | Título | Estado |
|----|------|-----------|---------------|--------|--------|
| H-01 | Migración | ALTO | V3/ (directorio eliminado) | Migración V2→V3 con 227 archivos sin commitear | abierto |
| H-02 | Gobernanza | ALTO | app/errors.py (fan_in=6) | Hub crítico sin PIN ni rule FUNDACIONAL | resuelto (P-09) |
| H-03 | Gobernanza | ALTO | app/decorators.py (fan_in=4) | Hub transversal sin PIN ni rule FUNDACIONAL | resuelto (P-10) |
| H-04 | Gobernanza | MEDIO | holy_projects.yaml | Gate de quality/approval bloqueado | resuelto |
| H-05 | Cobertura | MEDIO | tests/ | Ratio tests/módulos 0.141 < 0.20 (9 tests vs 64 módulos) | abierto |
| H-06 | Deprecación | MEDIO | app/ (14 usos) | datetime.utcnow() deprecado Python 3.14 | resuelto |
| H-07 | Auditoría | MEDIO | BUGS.md, .holy/ | Sin audit trail ni SIDC; BUGS.md vacío | resuelto |
| H-08 | Refactor | BAJO | app/routes/admin.py, app/cli/migrate_v2.py | Complejidad mccabe 41 y 46 respectivamente | abierto |
| H-09 | Despliegue | BAJO | .env.production | ADMIN_API_TOKEN missing_prod | abierto |

## Bugs de prueba holy-core

| ID | Categoría | Severidad | Ruta afectada | Título |
|----|-----------|-----------|---------------|--------|
| LEGAL-01 | Compliance | ALTO | app/models/participacion.py | Sin columnas de consentimiento (Ley 1581) | resuelto |
| LEGAL-02 | Compliance | ALTO | app/templates/participar.html | Sin checkbox de autorización de datos | resuelto |
| LEGAL-03 | Compliance | MEDIO | base.html footer | Links legales rotos (#) sin páginas reales | resuelto |
| LEGAL-04 | Compliance | MEDIO | app/routes/ | Sin endpoints ARCO ni páginas de tratamiento de datos | resuelto |
| LEGAL-05 | Compliance | BAJO | app/templates/base.html | Sin aviso de cookies | resuelto |

Formato de fila válida: `| ID | Categoría | Severidad | Ruta | Título |` con ID
que contenga guion (`HOLY-*`, `BUG-*`, `AUTO-*`, ...).
