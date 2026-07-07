# Laboratorio de Inteligencia Pública V3

## Sistema Nacional de Inteligencia Participativa

**Powered by Stonelytics**

### Descripción

Plataforma de inteligencia participativa para recolectar, organizar, clasificar y transformar propuestas ciudadanas en evidencia útil para la construcción del Plan Nacional de Desarrollo 2027–2030.

### Características Principales

- **Motor SRIE**: Clasificación automática de propuestas contra marco estratégico configurable
- **Formulario conversacional**: 5 pasos + resultado inmediato (no parece un formulario)
- **Modelo configurable**: Plan → Pilar → Línea → Componente → Objetivo → Indicador
- **Dashboard público**: Mapa SVG interactivo, charts, tendencias, top propuestas
- **Centro de Inteligencia**: 9 módulos de administración
- **Reutilizable**: Funciona para gobiernos, ONG, universidades, consultoras

### Stack Tecnológico

- **Backend**: Flask 3.1, SQLAlchemy 2.0, PostgreSQL 16, Redis 7, Gunicorn 23, Nginx
- **Frontend**: Jinja2, Bootstrap 5 (custom), Vanilla JS ES6, Chart.js 4
- **Seguridad**: CSRF, rate limiting, bleach sanitization, security headers, gzip
- **Infraestructura**: Docker Compose, multi-stage build, health checks

### Inicio Rápido

```bash
# 1. Clonar el repositorio
git clone <repo-url>
cd Construyamos_Colombia/V3

# 2. Crear .env
cp .env.example .env
# Editar .env con tus valores

# 3. Levantar con Docker
docker compose up -d

# 4. Sembrar datos
docker compose exec app flask seed

# 5. Abrir
https://l-inteligenciapublica.stonelytics.tech
```

### Desarrollo Local

```bash
# 1. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar
cp .env.example .env
# Editar .env

# 4. Sembrar datos
flask seed

# 5. Ejecutar
python run.py
```

### Estructura del Proyecto

```
V3/
├── app/
│   ├── models/          # Modelos de datos (Plan, Pilar, Participacion, etc.)
│   ├── routes/          # Blueprints (home, participar, admin, etc.)
│   ├── services/        # Lógica de negocio
│   │   └── srie/        # Motor de clasificación SRIE
│   ├── seed/            # Datos iniciales (18 pilares, 8 problemas)
│   ├── static/          # CSS (design system), JS (map, form)
│   └── templates/       # Templates Jinja2 (9 admin + 6 públicos)
├── nginx/               # Configuración Nginx
├── tests/               # Tests unitarios y de integración
├── docker-compose.yml
├── Dockerfile
├── config.py
├── deploy.sh
└── run.py
```

### Modelo Estratégico

```
Plan (configurable)
 └── Pilar (18 pilares del plan)
     └── Línea Estratégica
         └── Componente
             └── Objetivo
                 └── Indicador
```

### Motor SRIE

El motor clasifica automáticamente cada propuesta contra el plan estratégico:

1. **Matching por problema**: Problema real → Pilar (mapping directo)
2. **Cálculo de confianza**: 0.0 - 1.0 (alto/medio/bajo/sin clasificar)
3. **Explicación al ciudadano**: Texto claro sobre la clasificación

### Centro de Inteligencia (Admin)

9 módulos de administración:

| Módulo | Descripción |
|--------|-------------|
| Dashboard | Stats, tabla recientes |
| Participaciones | Lista, detalle, búsqueda, filtros, eliminación |
| Pilares | Lista, detalle, activar/desactivar |
| Problemas | Catálogo, activar/desactivar |
| Clasificaciones | Cola de revisión, filtrar por confianza |
| Planes | CRUD de planes estratégicos |
| Export | CSV, JSON |
| Config | Estado del sistema |
| Logs | Auditoría de participaciones |

### API Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/` | Página de inicio |
| GET | `/participar` | Formulario conversacional |
| GET | `/resultados` | Dashboard público |
| GET | `/iniciativa` | Página de la iniciativa |
| GET | `/api/problemas` | Catálogo de problemas |
| POST | `/api/enviar` | Enviar participación |
| GET | `/api/estadisticas` | Stats agregados |
| GET | `/api/participaciones` | Participaciones paginadas |
| GET | `/health` | Health check |
| GET | `/admin/login` | Login admin |
| GET | `/admin/` | Dashboard admin |

### Seguridad

- CSRF protection (Flask-WTF)
- Rate limiting: 5/min en `/api/enviar`, 10/min en `/admin/login`
- Input sanitization (bleach)
- Security headers (X-Content-Type-Options, X-Frame-Options, HSTS, etc.)
- Session HTTPOnly + SameSite + Secure (production)
- IP hashing (SHA-256)

### Testing

```bash
# Ejecutar todos los tests
pytest

# Con cobertura
pytest --cov=app --cov-report=html

# Solo unitarios
pytest tests/unit/

# Solo integración
pytest tests/integration/
```

### Credenciales Admin

- Usuario: `admin`
- Contraseña: `4h8KuTFbKZdrK7jKwR+DaQ==`

### Licencia

Proyecto privado — Stonelytics © 2026
