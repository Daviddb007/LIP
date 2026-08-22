# AGENTS.md — Contexto para agentes que trabajan en este proyecto

> Contexto mínimo para cualquier agente (TRINITY o externo) antes de tocar código.
> Complementa a `ALCANCEGLOBAL.md` (visión) y `PROJECT.md` (ADN técnico).

## Qué es esto

Laboratorio de Inteligencia Pública V3 — Sistema Nacional de Inteligencia
Participativa (Construyamos Colombia, powered by Stonelytics). Recolecta y clasifica
propuestas ciudadanas para el PND 2027–2030 vía motor SRIE. Flask + PostgreSQL +
Redis + Nginx. Áreas: participar, resultados/analítica, biblioteca, conocimiento,
laboratorio, administración (9 módulos).

## Reglas del proyecto (TRINITY)

- Leer `ALCANCEGLOBAL.md` + `PROJECT.md` antes de construir (P-ALC-01).
- No inventar precios ni métricas (P-PRC-01/P-PAU-02).
- Cambios de esquema requieren migración (P-DEP-06).
- No tocar producción sin GO humano (P-TRI-03); sin pruebas + verificación Holy.
- QA: pipes funcionales en verde antes de deploy (P-QA-01).

## Verificación

- Tests: `py -m pytest tests/ -v --tb=short`
- Lint: `ruff check`
