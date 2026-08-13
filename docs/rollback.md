# Plan de reversión — Milestone M0+M1 (Grupos Focales)

> **Aplica a**: commit del milestone "Estrategia de participación robusta" (M0
> infraestructura + M1 grupos focales: org → sesión → participante → audio →
> transcripción → grafo).
> **Propietario**: Centro Nacional de Inteligencia · aprobación compliance.

## 1. Evaluación previa (decisión de reversión)

Antes de revertir confirmar con `git status` que no hay trabajo local sin commitear
que se perdería, y verificar que el incidente que motiva la reversión está acotado
al milestone (fallo de migración, datos corruptos en grupos focales, regresión
de la UI de participación).

## 2. Reversión de código

```bash
# Opción A — revert en un commit nuevo (recomendada, preserva historia)
git revert --no-commit <commit_del_milestone>
git commit -m "revert: milestone M0+M1 grupos focales"

# Opción B — reset destructivo (solo si el milestone NO se ha desplegado)
git reset --hard <commit_anterior>
```

El commit del milestone toca: `config.py`, `run.py`, `requirements.txt`,
`docker-compose.yml`, `Dockerfile`, `.env.example`, `.env.production.example`,
`.gitignore`, `.dockerignore`, `app/__init__.py`, `app/models/{focal,grafo}.py`,
`app/services/{llm_client,transcripcion_service,grafo_service,worker_jobs}.py`,
`app/routes/focales.py`, `worker.py`, `app/templates/admin/focales/`,
`tests/test_focales.py`, `app/templates/admin/dashboard.html`,
`holy_projects.yaml`, `AUDITORIA_HOLY.md`, `ROADMAP.md`, `BUGS.md`,
`docs/rollback.md`.

## 3. Reversión de base de datos (PostgreSQL)

Backup previo (siempre): `pg_dump -Fc construyamos_v3 > pre_rollback.dump`.

Tablas nuevas del milestone (drop en orden de dependencias):

```sql
DROP TABLE IF EXISTS relaciones_grafo;
DROP TABLE IF EXISTS nodos_grafo;
DROP TABLE IF EXISTS segmentos_transcript;
DROP TABLE IF EXISTS transcripts_focales;
DROP TABLE IF EXISTS audios_focales;
DROP TABLE IF EXISTS preguntas_focales;
DROP TABLE IF EXISTS participantes_focales;
DROP TABLE IF EXISTS sesiones_focales;
DROP TABLE IF EXISTS orgs_focales;
```

Índices y constraints asociados se eliminan con las tablas. No se tocan tablas
preexistentes (participaciones, plan, catálogos, API tokens, etc.).

## 4. Reversión de configuración y entorno

- Quitar del `.env`/`docker-compose.yml` las variables del milestone:
  `UPLOADS_DIR`, `UPLOAD_MAX_MB`, `AUDIO_ALLOWED_EXTENSIONS`,
  `RQ_CONNECTION_URI`, `RQ_QUEUE_TRANSCRIPCION`, `RQ_QUEUE_ANALISIS`,
  `WHISPER_MODEL`, `WHISPER_DEVICE`, `WHISPER_COMPUTE_TYPE`,
  `LLM_PROVIDER`, `LLM_API_KEY`, `LLM_MODEL`, `LLM_EMBEDDING_MODEL`.
- `docker-compose.yml`: quitar el servicio `worker` y el volumen `uploads_data`.
- Reconstruir contenedores: `docker compose up -d --remove-orphans`.

## 5. Datos reservados (audios/documentos)

Los audios viven en el volumen `uploads_data` (fuera del web root). Para
revertir el **dato** (no solo el código):

```bash
docker compose stop worker app
docker volume rm construyamos_uploads_data     # IRREVERSIBLE — confirmar backup previo
```

En instalación local: borrar el directorio `uploads/` (o `tests/tmp_uploads/`).

## 6. Gobernanza holy-core

- Revertir `holy_projects.yaml` a la revisión anterior (quitar P-12 y la rule
  `worker.py`; restaurar el check `rollback` a `aprobado: false`).
- Registrar el incidente en `BUGS.md` con severidad y ejecutar
  `python holy_runner.py --once` para dejar evidencia en `.holy/`.

## 7. Criterio de éxito de la reversión

1. `venv/Scripts/python.exe -m pytest tests/ -q` → suite pre-milestone verde.
2. `venv/Scripts/python.exe -m pytest tests/test_holy_pins.py -q` → 13/13.
3. `python -m holy_core briefing --config holy_projects.yaml` → gate coherente.
4. App levanta y `/admin` responde sin referencias a `focales`.
5. Verificado que no quedan archivos huérfanos ni tablas del milestone.
