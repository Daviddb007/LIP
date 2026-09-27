# AUDITORÍA — Core de negocio de LIP (claridad semántica)

> Objetivo: definir con precisión qué ofrece el Laboratorio de Inteligencia Pública,
> quién es el cliente real y corregir la narrativa difusa de la página.

---

## 1. El problema de fondo (diagnóstico de la narrativa)

LIP hoy intenta ser **demasiadas cosas a la vez en la misma superficie**:

| Superficie | Qué ofrece | A quién |
|---|---|---|
| `/participar` | Participación ciudadana con clasificación SRIE | Ciudadano |
| `/resultados` `/analitica` | Observatorio / evidencia | Estado, investigadores |
| `/secop` | Visor de contratación pública | Empresas, consultores |
| `/secop/licitar` | Servicio de licitación (equipo profesional) | Empresas |
| `/biblioteca` | Políticas públicas navegables | Ciudadano, ONG, universidad |
| `/conocer` | Educación cívica | Ciudadano |
| `/asistente` | Asistente sobre el Estado | Ciudadano |
| `/saas` | SRIE Platform multi-tenant | Gobiernos, orgs (producto) |
| `/focales`, `/admin` | Herramientas internas | Equipo StoneLytics |

**Consecuencia:** la home dice "participa", pero no explica qué le entrega a cada
audiencia ni por qué LIP es distinto. No hay una frase que condense el valor.

## 2. Quién es el cliente (y quién NO)

**Cliente institucional (el que paga/contrata):**
- **Construyamos Colombia / proceso PND 2027–2030** — la implementación nacional.
- Mercado reutilizable: **gobiernos, ministerios, gobernaciones, ONG, universidades y
  consultoras** (vía SRIE Platform multi-tenant, `/saas`).

**Usuarios (no clientes, pero imprescindibles):**
- **Ciudadano** — aporta la voz (el insumo del sistema).
- **Tomador de decisión / equipo técnico de la entidad** — consume la evidencia.

**Nueva línea de ingreso (onda SECOP):**
- **Pymes y empresas que quieren contratar con el Estado** — consumen el visor SECOP
  y compran el servicio de licitación (`/secop/licitar`).

## 3. Propuesta de valor — la frase que falta

El core de LIP se puede resumir en **una frase**:

> **"LIP convierte la voz de Colombia en evidencia para decidir — y abre la
> contratación pública para que las empresas entren al Estado con datos."**

Dos motores, un solo sistema:
1. **Inteligencia participativa** (SRIE): la voz ciudadana → clasificada → pública.
2. **Inteligencia de contratación** (SECOP): los procesos públicos → visibles → accesibles.

## 4. La narrativa correcta por audiencia

| Audiencia | Mensaje correcto | Dónde |
|---|---|---|
| **Ciudadano** | "Tu voz no se pierde: se clasifica contra el plan y queda pública." | Home, Participar |
| **Estado / entidad** | "Evidencia accionable de lo que el país pide, para priorizar con datos." | Home, Observatorio |
| **Empresa** | "Los procesos SECOP abiertos, filtrados por pilar — y un equipo que licita por ti." | Home, SECOP, Licitación |
| **Institución / ONG** | "La misma plataforma, con tu marco estratégico (SRIE Platform)." | Home, SaaS |

## 5. Problemas de claridad detectados en la home actual

1. **El hero no dice "para quién".** "El país se construye escuchándolo" es emotivo pero
   no informa qué recibe el visitante. Falta el "qué te entregamos" (evidencia / datos /
   contratación).
2. **No hay una sección de audiencias.** No se dice quién usa LIP y para qué.
3. **SECOP aparece como una página suelta**, no como parte del mismo sistema de
   "inteligencia pública". La licitación (servicio de pago) está casi escondida en nav.
4. **El SaaS está desconectado de la narrativa** (la plataforma reutilizable no se
   explica como el "motor detrás").
5. **Copy difuso en secciones secundarias** (iniciativa mezcla "problema/solución"
   con datos sin fuente clara: "solo el 12%..." sin respaldo).

## 6. Mejoras priorizadas (después de esta auditoría)

1. **Home: bloquecito de "para quién es"** — 3 tarjetas con audiencia (Ciudadano /
   Estado / Empresa) y su mensaje exacto.
2. **Hero: sub-línea de valor concreta** — "Evidencia para decidir. Contratación
   abierta para competir. Tu voz para construir."
3. **SECOP + Licitación integrados a la narrativa** — explicitar que son parte de la
   inteligencia pública, no un módulo aparte.
4. **SaaS explicado como el motor reutilizable** (SRIE Platform) en una sección "El motor".
5. **Auditar copy con datos sin fuente** (el "12%" de iniciativa) → citar o quitar.
6. **Metas/titles de páginas alineadas a la propuesta de valor** (SEO semántico).

*TRINITY · AUDITORÍA DE NÚCLEO DE NEGOCIO LIP · 2026-09-27*
