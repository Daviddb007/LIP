# CONSTRUYAMOS COLOMBIA

## Ecosistema Nacional de Inteligencia Pública

### Powered by StoneLytics · Tecnología SRIE

---

## Visión

> **Laboratorio de Inteligencia Pública** no es una plataforma de participación ciudadana. Es un **Ecosistema de Inteligencia Pública** desarrollado por **StoneLytics** para conectar ciudadanía, conocimiento, evidencia y toma de decisiones mediante tecnología e inteligencia artificial.

El ecosistema conecta cuatro grandes mundos:

```
Ciudadanía → Conocimiento Público → Inteligencia Estratégica → Toma de Decisiones
```

Todo el ecosistema gira alrededor del motor **SRIE (Sistema de Recolección e Inteligencia Estratégica)**, el núcleo encargado de transformar información en conocimiento estructurado.

---

## Principios

Toda funcionalidad debe cumplir:

- **Utilidad pública** — Resuelve un problema real
- **Lenguaje ciudadano** — Sin tecnicismos excluyentes
- **Transparencia** — Trazabilidad total de la información
- **Simplicidad** — Experiencias intuitivas
- **Reutilización** — Componentes modulares
- **Evidencia** — Decisiones basadas en datos
- **Escalabilidad** — Arquitectura preparada para crecer
- **Accesibilidad** — Para todos los colombianos

---

## Estado Actual (MVP)

El proyecto ya dispone de:

- [x] Participación ciudadana multipaso
- [x] Motor SRIE de clasificación estratégica
- [x] Dashboard de resultados
- [x] Panel administrativo
- [x] Arquitectura Docker
- [x] PostgreSQL + Redis
- [x] Nginx + Gunicorn
- [x] Infraestructura lista para producción

### Milestone M0+M1 — Grupos Focales (2026-08-13)

Estrategia de participación robusta **completada y verificada** (ver `AUDITORIA_HOLY.md`):

- [x] Organizaciones → sesiones → participantes → preguntas guía
- [x] Audios reservados (volumen local, whisper local; la nube solo recibe texto)
- [x] Transcripción en cola Redis/RQ con CLI `flask transcribir-pendientes`
- [x] Grafo de conceptos (Cytoscape.js en admin) + export HTML + CLI `flask construir-grafos`
- [x] API interna del módulo + 17 tests (suite total 179/179) + PIN P-12 preventivo
- [x] Plan de reversión: `docs/rollback.md`

> **Desviación documentada**: el proyecto no usa Alembic; patrón `db.create_all()` en run.py/deploy. Aplica únicamente a `create_engine` de app/DB (ver AUDITORIA_HOLY.md).

---

## Fase 1: Participación Inteligente

**Objetivo:** Convertir el formulario actual en una experiencia conversacional. El ciudadano nunca debe sentir que diligencia una encuesta; debe sentirse acompañado.

> **Estado (2026-08-13):** Implementado y verificado end-to-end (wizard 5 pasos en `/participar` → clasificación SRIE top-3 con explicación → resultados públicos). La variante **conversacional** (chat guiado en vez de formulario) queda documentada como mejora futura: el motor de clasificación, los catálogos y la explicación automática ya son reutilizables desde un chat, pero la UX conversacional no está construida.

### Alcance

- [x] Selección de hasta 3 grandes temas
- [x] Problemas por cada tema
- [x] Contexto ciudadano
- [x] Propuesta
- [x] Actores responsables
- [x] Beneficiarios
- [x] Clasificación SRIE con explicación automática
- [x] Visualización del resultado
- [x] Experiencia premium responsive
- [ ] Experiencia conversacional (chat guiado) — mejora futura

### Producto esperado

El ciudadano entiende que su participación fue analizada y clasificada.

---

## Fase 2: Centro de Conocimiento Público

**Objetivo:** Construir un espacio interactivo para explicar cómo funciona el Estado colombiano. No será un repositorio documental; será una plataforma educativa en lenguaje sencillo, visual e interactivo.

> **Estado (2026-08-13):** Sin implementación verificada como centro de conocimiento. La landing `/iniciativa` (iniciativa.html) divulgó la iniciativa y el motor, y el asistente (`/asistente`, F5) responde sobre entidades/instrumentos, pero el módulo educativo interactivo (políticas públicas, timeline, glosario, casos) **no está construido**. Pendiente real.

### Módulos

- [ ] **¿Qué es una política pública?** — Concepto, video, infografía, ejemplos, caso práctico
- [ ] **¿Cómo nace una política pública?** — Timeline interactivo: Problema → Agenda → Diagnóstico → Formulación → Implementación → Seguimiento → Evaluación → Mejoramiento
- [ ] **Instrumentos del Estado** — PND, CONPES, Leyes, Decretos, Políticas Públicas, Programas, Proyectos, Planes territoriales, ODS, Indicadores
- [ ] **Glosario interactivo** — Cada concepto enlaza otros (como Wikipedia, pero más visual)
- [ ] **Casos reales** — Ejemplos colombianos documentados

### Producto esperado

Cualquier ciudadano debe comprender cómo funciona una política pública en menos de 15 minutos.

---

## Fase 3: Biblioteca Inteligente

**Objetivo:** Transformar las políticas públicas en información navegable. No PDFs. Información viva. Cada política tendrá su propia página.

> **Estado (2026-08-13):** Implementado. Modelo `Politica` con 17 campos, `/biblioteca` con filtros (estado/sector), detalle `/biblioteca/<id>`, API `/api/politicas` y consulta con SRIE (`/api/politicas/<id>/preguntar`). Tests: `tests/test_biblioteca.py`.

### Cada ficha incluirá

- [x] Resumen ejecutivo
- [x] Problema que resuelve
- [x] Objetivos
- [x] Población objetivo
- [x] Normatividad
- [x] Cronología
- [x] Entidades responsables
- [x] Indicadores
- [x] Presupuesto
- [x] Estado
- [x] Documentos
- [x] ODS relacionados
- [ ] Mapa territorial
- [ ] Línea de tiempo
- [x] **"Hacer preguntas"** utilizando SRIE

### Producto esperado

La política pública deja de ser un documento. Se convierte en una experiencia interactiva.

---

## Fase 4: Observatorio Nacional

**Objetivo:** Visualizar qué está ocurriendo en Colombia. No solamente mostrar estadísticas. Mostrar inteligencia.

> **Estado (2026-08-13):** Implementado como observatorio en `/resultados` (mapa nacional con `map.js`, estadísticas, top problemas/actores/beneficiarios/pilares) + `/analitica` (series de tiempo, territorio, comparativos, clustering, predicciones). Tests: `tests/test_analitica.py`, `tests/integration/test_api.py`.

### Dashboard

- [x] Mapa nacional / departamental / municipal
- [x] Series de tiempo
- [x] Problemas, prioridades y pilares
- [x] Comparativos y brechas
- [x] Actores y beneficiarios
- [ ] Heatmaps
- [x] Indicadores en tiempo real

### Producto esperado

El primer observatorio ciudadano alimentado en tiempo real.

---

## Fase 5: Asistente Público SRIE

**Objetivo:** Crear un asistente conversacional especializado en el Estado colombiano. No será ChatGPT; será un especialista.

> **Estado (2026-08-13):** Implementado. `/asistente` con motor de conocimiento oficial (23 entradas: entidades, instrumentos, participación, políticas) y API `/api/asistente/preguntar`. Tests: `tests/test_asistente.py`.

### Capacidades

- ¿Qué hace un CONPES?
- ¿Qué políticas existen sobre discapacidad?
- ¿Qué programas existen para jóvenes?
- ¿Qué entidades trabajan en seguridad?
- ¿Qué dice el PND sobre vivienda?
- ¿Cómo participo?
- ¿Qué ministerio lidera esto?

Todas las respuestas utilizando únicamente información oficial.

### Producto esperado

El ciudadano conversa con el Estado.

---

## Fase 6: Motor de Armonización Estratégica

**Objetivo:** Comparar automáticamente participación ciudadana, planes, políticas, programas, ODS, planes de gobierno y planes territoriales.

> **Estado (2026-08-13):** Implementado. `/armonizacion` con matriz de cobertura, coincidencias, vacíos/brechas, oportunidades y análisis ODS. API `/api/armonizacion` + `/api/v1/armonizacion`. Tests: `tests/test_armonizacion.py`.

SRIE identificará:

- [x] Coincidencias
- [x] Vacíos
- [x] Brechas
- [x] Oportunidades

### Producto esperado

Construcción automática de matrices de armonización.

---

## Fase 7: Laboratorio de Innovación Pública

**Objetivo:** Permitir experimentar escenarios y simulaciones.

> **Estado (2026-08-13):** Implementado. `/laboratorio` con simulación de presupuesto, redistribución sectorial y nuevos sectores (índice de armonía base vs simulado). API `/api/laboratorio/estado` y `/api/laboratorio/simular`. Tests: `tests/test_laboratorio.py`.

- ¿Qué pasaría si aumenta el presupuesto?
- ¿Qué pasa si cambia una prioridad?
- ¿Cómo cambian las necesidades?

### Producto esperado

Laboratorio de simulación para investigadores y tomadores de decisiones.

---

## Fase 8: Analítica Avanzada

**Objetivo:** Incorporar analítica e inteligencia artificial al ecosistema.

- [x] Nube de palabras
- [x] Clustering (semántico por embeddings + coseno, degradación a hashing local)
- [x] Embeddings (LLM si está configurado; fallback local sin dependencias ML)
- [x] Análisis semántico (tema dominante por mes en tendencias)
- [x] Detección de tendencias
- [x] Análisis territorial
- [x] Comparaciones
- [x] Predicciones

### Producto esperado

SRIE evoluciona hacia inteligencia estratégica.

---

## Fase 9: Centro Administrativo (Centro Nacional de Inteligencia)

> **Estado (2026-08-13):** Implementado en `/admin` (dashboard con indicadores + alertas operativas, CRUD participaciones/sectores/actores/beneficiarios/pilares/problemas, clasificaciones, planes, export CSV/JSON, config, logs). Tests: `tests/integration/test_api.py`, `tests/test_export.py`, `tests/test_alertas.py`. Pendiente: gestión de políticas y usuarios en el admin.

- [x] Participaciones
- [ ] Políticas
- [ ] Usuarios
- [x] Clasificaciones
- [x] Alertas
- [x] Reportes
- [x] Indicadores
- [x] Configuración
- [x] Logs
- [x] Exportaciones
- [x] Monitoreo

---

## Fase 10: API Pública

> **Estado (2026-08-13):** Implementado. API REST `/api/v1` con spec OpenAPI 3.0.3 (`/api/v1/openapi.json`), Swagger UI (`/api/docs/swagger`), docs custom (`/api/docs`), versionado v1 y tokens con roles (lectura/escritura/admin) vía `ApiToken`. Tests: `tests/test_api_v1.py`.

- [x] API REST con Swagger
- [x] Documentación
- [x] Versionamiento
- [x] Tokens y permisos

---

## Fase 11: Ecosistema Abierto

> **Estado (2026-08-13):** Implementado el ecosistema de integraciones en `/ecosistema` (partners: Ministerio, DNP, Gobernaciones, etc.) con webhooks CRUD (`/api/webhooks`) y despacho de eventos (`dispatch`). Tests: `tests/test_integraciones.py`.

Permitir integrar:

- [x] Ministerios
- [x] Gobernaciones
- [x] Alcaldías
- [x] Universidades
- [x] Centros de pensamiento
- [x] ONG
- [x] Cooperación internacional

---

## Fase 12: Plataforma SaaS StoneLytics

**Objetivo:** Convertir Laboratorio de Inteligencia Pública en un producto comercial multi-tenant. Cada cliente podrá crear su propio portal, plan, políticas, observatorio, SRIE y dashboard sin modificar el código.

> **Estado (2026-08-13):** Implementado el **multi-tenant básico**: registro de organización (plan/tipo/email/color), landing pública por slug (`/saas/<slug>`) y API de organizaciones. Pendiente como iteración futura: aislamiento completo por tenant (políticas, observatorio, SRIE y dashboard propios por organización). Tests: `tests/test_saas.py`.

### Arquitectura de Producto

```
SRIE Platform (producto SaaS)
  └── Laboratorio de Inteligencia Pública (implementación nacional → caso de éxito)
  └── Cliente N (gobernación, ministerio, universidad...)
```

**SRIE** es el motor tecnológico (el producto SaaS de StoneLytics). **Laboratorio de Inteligencia Pública** es la implementación nacional que demuestra sus capacidades. Mañana se puede desplegar la misma tecnología para cualquier organización cargando un nuevo marco estratégico y una nueva identidad visual.

---

## Diseño

### Inspiración

Stripe · Linear · Notion · Apple · Gov.uk · Vercel

### Lineamientos

- **Institucional** — Seriedad y confianza
- **Premium** — Calidad de producto
- **Minimalista** — Menos es más
- **Tecnológico** — Sensación moderna
- **Mucho espacio** — Composición aireada
- **Animaciones discretas** — Sutiles, no distractoras
- **Excelente accesibilidad** — Para todos

---

## Filosofía Final

Laboratorio de Inteligencia Pública no debe convertirse en otro portal del Estado. Debe convertirse en el **primer Ecosistema Colombiano de Inteligencia Pública**, donde cualquier ciudadano pueda **aprender**, **participar**, **consultar**, **comparar**, **proponer** y **comprender** cómo se construyen las decisiones públicas.

El motor **SRIE** será el corazón del ecosistema, transformando información dispersa en conocimiento estructurado para fortalecer la formulación de políticas públicas, la armonización de planes de desarrollo, la generación de evidencia y la toma de decisiones basada en datos.

---

## Licencia

Laboratorio de Inteligencia Pública — StoneLytics © 2026
