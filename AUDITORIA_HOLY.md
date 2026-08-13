# Auditoría holy-core — Laboratorio de Inteligencia Pública (LIP)

- **Fecha**: 2026-08-05
- **Tooling**: holy-core `0.7.0` (editable en `venv/`, vivo desde `~/HOLY/holy-core/src`)
- **Alcance**: diagnóstico read-only (scanner, gobernanza, tests, despliegue). Sin remediación.
- **Método**: `ScannerEngine`, `ComplexityScorer`, `CodeGraphBuilder`, `MultiProjectConfig`/`briefing`, `test_holy_pins.py`, suite completa `pytest`, `DeploymentChecker`.

---

## 1. Resumen ejecutivo

| Área | Estado | Evidencia |
|---|---|---|
| Madurez | **CRECIMIENTO** (no MADURO) | 3 capas (models/routes/services), ratio tests **0.141 < 0.20** |
| Tests | **144/144 verdes** | 131 (unit+integration) + 13 `test_holy_pins` |
| Hubs (fan_in≥3) | **14 módulos** | `app/__init__.py`=29, `models/*`=3..19 |
| Gobernanza | 8 PINs; **4 hubs sin PIN** | `errors.py`(6), `decorators.py`(4), `analitica_service`(3), `armonizacion_service`(3) |
| Complejidad | **6 módulos COMPLEJOS** | `armonizacion_service` 0.683, `__init__.py` 0.669, `analitica_service` 0.639, `admin.py` 0.633, `migrate_v2` 0.623, `api_v1` 0.615 |
| Gate de calidad | **Bloqueado** | checks de `quality_phases` y `approval_areas` todos `aprobado: false` |
| Repo | **227 archivos sin commitear** | 127 `D` (V3/), 65 `M`, 35 `??` — migración V2→V3 no commiteada |
| Deprecaciones | **14 usos de `datetime.utcnow()`** | deprecado en Python 3.14 |
| Audit trail | **Sin historial** | `.holy/` no existe |
| BUGS.md | Sin bugs de prueba | pipeline SIDC no ejercitable aún |
| Git sync | HEAD == origin/master | 0 ahead / 0 behind (pero 227 dirty) |

**Conclusión**: LIP es una app funcional y bien testeada (verde 100%), con gobernanza declarada que en su mayoría coincide con la evidencia del scanner. Los riesgos principales son: **cambio sin commitear de la migración V3**, **hubs compartidos sin PIN** (`errors.py`, `decorators.py`), **gate de calidad/approval bloqueado** y **ratio de tests bajo para el umbral de MADURO**.

---

## 2. Scanner estático

### 2.1 Madurez
- Nivel: **crecimiento** — falta ratio de tests ≥ 0.20 para MADURO (hoy 0.141: 9 módulos de test / 64 módulos).
- 64 módulos, 7.081 líneas, 9 módulos de test, 3 capas reconocidas (models 9, routes 16, services 17).

### 2.2 Hubs (fan_in ≥ 3) — 14 módulos
| Ruta | fan_in | fan_out | Categoría rule |
|---|---|---|---|
| `app/__init__.py` | 29 | 17 | FUNDACIONAL |
| `app/models/catalog.py` | 19 | 1 | FUNDACIONAL |
| `app/models/participacion.py` | 14 | 2 | FUNDACIONAL |
| `app/models/plan.py` | 11 | 1 | FUNDACIONAL |
| `app/models/politica.py` | 9 | 1 | FUNDACIONAL |
| `app/errors.py` | 6 | 0 | **catch-all `**`** |
| `app/decorators.py` | 4 | 1 | **catch-all `**`** |
| `app/models/miembro.py` | 4 | 1 | FUNDACIONAL |
| `app/models/webhook.py` | 4 | 1 | FUNDACIONAL |
| `app/models/api_token.py` | 3 | 1 | FUNDACIONAL |
| `app/models/organizacion.py` | 3 | 1 | FUNDACIONAL |
| `app/services/analitica_service.py` | 3 | 5 | ESTRATEGICO |
| `app/services/armonizacion_service.py` | 3 | 5 | ESTRATEGICO |
| `app/services/srie/classifier.py` | 3 | 6 | ESTRATEGICO |

### 2.3 Complejidad
Baseline calibrado (p90): líneas 273, mccabe 35, fan_in 4.

**6 módulos COMPLEJOS** (score ≥ 0.60):

| Módulo | score | líneas | mccabe | anid. |
|---|---|---|---|---|
| `app/services/armonizacion_service.py` | 0.683 | 273 | 32 | 6 |
| `app/__init__.py` | 0.669 | 176 | 23 | 5 |
| `app/services/analitica_service.py` | 0.639 | 287 | 26 | 5 |
| `app/routes/admin.py` | 0.633 | 473 | 41 | 4 |
| `app/cli/migrate_v2.py` | 0.623 | 239 | **46** | 4 |
| `app/routes/api_v1.py` | 0.615 | 177 | 35 | 4 |

Otros de atención: `seed_plan.py` (541 líneas, 25 mccabe), `validation.py` (161, 39 mccabe), `stats_service.py` (213), `srie/keywords.py` (277, diccionario de datos, mccabe 0).

### 2.4 Codegraph
- 743 nodos, 2.158 aristas (1.884 `llama_a`, 245 `accede_campo`, 29 `hereda_de`).
- Símbolos más referenciados son builtins/SQLAlchemy (`get` 204, `all` 74, `count` 72, `route` 71…).
- **Limitación**: `quien_llama_a` no resuelve imports cross-módulo (los nodos de `app.errors`/`app.decorators` no aparecen como destino). La evidencia fiable de acoplamiento es el fan_in por imports del §2.2.

---

## 3. Gobernanza declarada vs evidencia

Config canónica `holy_projects.yaml` cargada correctamente (13/13 `test_holy_pins`). 8 PINs, 13 classification_rules, 2 quality_phases, 3 approval_areas.

### 3.1 PINs existentes
| PIN | Severidad | Área | ¿Protege algún hub real? |
|---|---|---|---|
| P-01 | CRITICO | `app/models/` | Sí (catalog 19, participacion 14, plan 11, politica 9, miembro 4, webhook 4, api_token 3, organizacion 3) |
| P-02 | ALTO | `config.py` | No (fan_in 1 — bajo) |
| P-03 | CRITICO | `app/__init__.py` | Sí (hub #1, fan_in 29) ✓ |
| P-04 | ALTO | `app/services/srie/` | Sí (classifier 3, matcher 2) |
| P-05 | ALTO | `app/routes/api_v1.py` | Parcial (fan_in 1 pero fan_out 9 — dependencia externa amplia) |
| P-06 | MEDIO | `app/templates/` | No medible por scanner (HTML) |
| P-07 | MEDIO | `tests/` | No es hub |
| P-08 | CRITICO | `.env` | No es hub (secreto) |

### 3.2 GAPS detectados
1. **`app/errors.py` (fan_in 6) — SIN PIN y sin rule propia.** Lo importan `app`, `decorators`, `participar`, `asistente_service`, `validation`, tests. Es infraestructura compartida (errores de API globales); cae en el catch-all `**` como ESTRATEGICO, pero por perfil (como `__init__.py`) debería ser FUNDACIONAL.
2. **`app/decorators.py` (fan_in 4) — SIN PIN.** Lo importan 4 rutas (admin, integraciones, participar, saas); contiene decoradores de auth/seguridad. Misma situación: infra compartida sin protección declarada.
3. **`analitica_service` y `armonizacion_service` (fan_in 3)** — sin PIN específico, pero sí cubiertos por `app/services/**` ESTRATEGICO. Riesgo menor.

### 3.3 Classification rules
- Cobertura FUNDACIONAL solo para `app/models/**`, `app/__init__.py`, `config.py`, `.env`.
- `app/errors.py` y `app/decorators.py` no tienen rule propia → se clasifican por el catch-all `**` (ESTRATEGICO → repairman), cuando su perfil de hub de infraestructura sugiere FUNDACIONAL → directorsboard.

### 3.4 Gate de calidad y aprobaciones
- `quality_phases`: `desarrollo` (tests pasan) y `produccion` (sin secrets) — **ambos checks `aprobado: false`**.
- `approval_areas`: `compliance`, `calidad`, `rollback` — **todos `aprobado: false`**.
- Efecto: el pipeline SIDC nunca pasaría el gate; los checks se marcan en runtime cuando el humano aprueba, pero hoy nada los activa.

---

## 4. Validación de tests

- **144/144 passed** en 1.15s. Distribución:
  - `tests/integration/test_api.py`: 55
  - `tests/integration/test_features.py`: 34
  - `tests/test_holy_pins.py`: 13
  - `tests/unit/test_srie.py`: 22
  - `tests/unit/test_validation.py`: 20
- **Cobertura por hubs**: los hubs `errors`, `decorators`, `analitica_service`, `armonizacion_service` no tienen suite unitaria dedicada; se ejercitan indirectamente vía integración (test_api/test_features). `test_validation` importa `errors` (cobertura parcial).
- **Warnings (8)**: `datetime.datetime.utcnow()` deprecado en Python 3.14 — 14 usos en `app/` (6 modelos, `stats_service:184`, `admin.py:49/68`, `migrate_v2:136`, `participacion`, `plan`, etc.). SQLAlchemy también lo avisa al construir el schema.

---

## 5. Despliegue (`DeploymentChecker`)

### 5.1 Git sync
- HEAD == `origin/master` (0 ahead / 0 behind). El check compara commits, no working tree.
- **Hallazgo**: **227 archivos sin commitear** (127 `D` de `V3/`, 65 `M`, 35 `??`) — toda la migración V2→V3 sigue sin commit. El último commit local y remoto es `5458dfe`.

### 5.2 Env sync (`.env` vs `.env.production`) — 11 claves
| Clave | Estado | Nota |
|---|---|---|
| `ADMIN_API_TOKEN` | **missing_prod** | existe solo en local |
| `ADMIN_PASS` | diferente | local `admin123` (dev) vs producción (hash) ✓ esperado |
| `ADMIN_USER` | igual | |
| `CACHE_REDIS_URL`, `CACHE_TYPE` | missing_local | prod usa RedisCache; dev usa defaults ✓ esperado |
| `DATABASE_URL` | diferente | sqlite dev vs postgres prod ✓ esperado |
| `FLASK_CONFIG` | diferente | development vs production ✓ esperado |
| `LOG_LEVEL`, `PORT`, `RATELIMIT_STORAGE_URI` | missing_local | ✓ esperado |
| `SECRET_KEY` | diferente | ✓ esperado |

Diferencias mayormente esperadas dev/prod. Único punto de atención: `ADMIN_API_TOKEN` sin contraparte en producción.

### 5.3 Schema / blueprint / config sync
- **Vacíos, pero por limitación del tooling**: `check_schema_sync` asume `{root_name}.models.Base` (→ `lip.models`), pero LIP usa `app.models` + `db = SQLAlchemy()` declarative → el check se salta en silencio. Igual para blueprint. No es un hallazgo de la app.

### 5.4 Audit trail
- `.holy/` no existe → sin memoria institucional, sin `loop.log`, sin propuestas. `MetaHealthEngine`/`--status` no tienen historial que reportar.

---

## 6. Hallazgos priorizados

| # | Severidad | Hallazgo | Evidencia |
|---|---|---|---|
| H1 | **ALTO** | Migración V2→V3 sin commitear (227 archivos: 127 D, 65 M, 35 ??) | `git status`; HEAD==origin pero working tree diverge totalmente |
| H2 | **ALTO** | `app/errors.py` (fan_in 6) sin PIN ni rule FUNDACIONAL | scanner hubs + briefing |
| H3 | **ALTO** | `app/decorators.py` (fan_in 4) sin PIN ni rule FUNDACIONAL | scanner hubs + briefing |
| H4 | **MEDIO** | Gate de calidad/approval bloqueado (checks `aprobado: false`) | briefing |
| H5 | **MEDIO** | Ratio de tests 0.141 < 0.20 → madurez CRECIMIENTO, no MADURO | scanner |
| H6 | **MEDIO** | `datetime.utcnow()` deprecado (14 usos) | pytest warnings |
| H7 | **MEDIO** | Sin audit trail (`.holy/` no existe) y BUGS.md sin bugs de prueba → SIDC no ejercitado | filesystem |
| H8 | **BAJO** | 6 módulos COMPLEJOS (admin.py 473 líneas/mccabe 41, seed_plan 541, migrate_v2 mccabe 46) | complexity |
| H9 | **BAJO** | `ADMIN_API_TOKEN` missing en producción | env sync |

---

## 7. Recomendaciones (no aplicadas — fase posterior)

1. **Commitear la migración V3** (revisar antes los 65 `M` y los 35 `??`; no subir secrets; los `D` de `V3/` son el borrado esperado).
2. **Declarar PINs nuevos** en `holy_projects.yaml`: P-09 `app/errors.py` (ALTO/CRITICO) y P-10 `app/decorators.py` (ALTO), con rules FUNDACIONALes (destino `directorsboard`).
3. **Activar el gate**: marcar `aprobado: true` en `quality_phases`/`approval_areas` que efectivamente se cumplen (tests, sin secrets) o diseñar el flujo de aprobación.
4. **Subir ratio de tests a ≥ 0.20**: añadir suites unitarias a `analitica_service`, `armonizacion_service`, `errors`, `decorators`, `stats_service`.
5. **Reemplazar `datetime.utcnow()`** por `datetime.now(UTC)` (Python 3.14).
6. **Poblar BUGS.md** con bugs de prueba y ejecutar `holy_runner.py --once` para generar el primer audit trail (`.holy/`).
7. **Refactor candidatos**: descomponer `admin.py` (473 líneas), `seed_plan.py` (541), `migrate_v2.py` (mccabe 46).

---

## 8. Limitaciones del tooling (para interpretación)

- **Codegraph**: `quien_llama_a` no resuelve imports cross-módulo; el fan_in por imports (§2.2) es la métrica fiable.
- **DeploymentChecker**: schema/blueprint sync asumen layout `{root}.models`/`Base`; LIP (`app.models`) se salta esos checks.
- **Scanner**: cuenta `holy_runner.py`, `generate_password.py`, etc. como módulos (64 total); sin servidor Ollama/OpenRouter la clasificación del loop sería heurística.
- **`test_holy_pins.py`** exige que existan `holy_projects.yaml` y `holy_runner.py` en la raíz — son ficheros locales de integración, correctamente ignorados por git.

---

# Auditoría 2026-08-13 — Milestone M0+M1 "Grupos Focales" (verificación pre-commit)

- **Tooling**: holy-core `0.7.0` · `ScannerEngine`, `briefing`, `test_holy_pins`, suite `pytest`, `DeploymentChecker`.
- **Alcance**: verificación de todo lo creado en el milestone + gobernanza previa al commit.

## Resultados

| Área | Estado | Evidencia |
|---|---|---|
| Tests | **179/179 verdes** | 166 (unit+integration) + 13 `test_holy_pins` |
| Scanner | Madurez **crecimiento** | 75 módulos, 9.468 líneas, 11 módulos de test |
| Hubs nuevos del módulo | **2** (CRITICO) | `app/models/focal.py` (fan_in 6), `app/models/grafo.py` (fan_in 6) — cubiertos por P-01 |
| PIN nuevo | **P-12** (ALTO) | Protección preventiva del pipeline focales + worker |
| Gate de calidad | **Activado** | `produccion` (sin secrets) ✓, `calidad` (179/179) ✓, `rollback` (docs/rollback.md) ✓ |
| Secrets | **Sin hallazgos** | `.env` no trackeado; `.env.example`/`.env.production.example` solo placeholders |
| Audit trail | **Generado** | `.holy/memory.json` (vía `holy_runner.py --once`) |
| Bugs corregidos | **6** (H-10..H-15) | ver BUGS.md |
| Bugs de prueba SIDC | **FOCAL-01..04** añadidos | pipeline ejercitado (1 escalado, 8 omitidos) |

## Hallazgos corregidos en este milestone (read-only → remediación)

1. **H-10** `docker-compose.yml`: volumen `uploads_data` duplicado en `app` + faltaba
   `RQ_CONNECTION_URI`/whisper/LLM en la app web.
2. **H-11** Integridad FK PostgreSQL: sin `ondelete` en `relaciones_grafo`,
   `nodo.transcript_id/sesion_id`, `segmento.audio_id`, `audio.transcript_id` →
   IntegrityError al borrar transcript/sesión (SQLite no lo detecta en tests).
3. **H-12** `procesar_audio` duplicaba transcript al reprocesar audio transcrito
   (guard `transcript_id` + ruta `reprocesar` bloquea estado `transcrito`).
4. **H-13** Archivos de audio huérfanos al eliminar sesión/org (limpieza de
   directorio `uploads/sesion_X`).
5. **H-14** `int(org_id)`/`int(sector_id)` sin validar → 500.
6. **H-15** `coseno()` era producto punto → normalizado (afecta embeddings LLM).

## Decisión de arquitectura (desviación documentada)

- **Migraciones**: el proyecto no usa Alembic; sigue el patrón `db.create_all()`
  (run.py `seed`, deploy-docker.sh). El milestone mantiene ese patrón. Consecuencia:
  los `ondelete` añadidos solo aplican a bases nuevas; en una BD existente hay que
  recrear las tablas focales (`DROP`+`create_all`) o aplicar DDL manual.
- **Reserva total**: audios guardados en volumen `uploads_data` fuera del web root;
  transcripción con whisper local (los audios nunca salen del servidor); a la nube
  solo va texto (LLM_PROVIDER gemini/openai, default `ninguno` con fallback local).

## Limitaciones

- El `--once` de SIDC escaló LEGAL-01 (requiere humano): sin Ollama/OpenRouter la
  clasificación es heurística (limitación ya documentada en la auditoría anterior).
- Scanner: `quien_llama_a` no resuelve imports cross-módulo; el fan_in por imports
  (§2.2) sigue siendo la métrica fiable.

---

## Anexo: comandos utilizados

```
venv/Scripts/python.exe -c "<ScannerEngine.escanear()>"
venv/Scripts/python.exe -c "<ComplexityScorer.calibrate()+compute()>"
venv/Scripts/python.exe -c "<CodeGraphBuilder.construir()+CodeGraphIndex>"
python -m holy_core briefing --config holy_projects.yaml
venv/Scripts/python.exe -m pytest tests/test_holy_pins.py -q
venv/Scripts/python.exe -m pytest tests/ -q
venv/Scripts/python.exe -c "<DeploymentChecker.check_all()>"
git status / git rev-list --left-right --count origin/master...HEAD
```
