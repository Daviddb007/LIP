"""Spec OpenAPI 3.0 de la API REST pública v1.

Se genera en Python para mantenerse sincronizada con app/routes/api_v1.py.
Se sirve en GET /api/v1/openapi.json y la consume la UI Swagger de /api/docs.
"""
from __future__ import annotations

from typing import Any


def spec_openapi() -> dict[str, Any]:
    return {
        "openapi": "3.0.3",
        "info": {
            "title": "Laboratorio de Inteligencia Pública API",
            "description": (
                "API REST pública del Ecosistema Nacional de Inteligencia Pública. "
                "Los endpoints que requieren token usan el esquema Bearer con un ApiToken "
                "generado en POST /api/v1/token."
            ),
            "version": "1.0.0",
            "contact": {"name": "Centro Nacional de Inteligencia"},
        },
        "servers": [{"url": "/api/v1", "description": "Base de la API v1"}],
        "tags": [
            {"name": "Ecosistema", "description": "Estadísticas y analítica general"},
            {"name": "Datos", "description": "Participaciones, políticas y sectores"},
            {"name": "SRIE", "description": "Clasificación estratégica"},
            {"name": "Tokens", "description": "Gestión de tokens de acceso"},
        ],
        "paths": {
            "/": {
                "get": {
                    "tags": ["Ecosistema"],
                    "summary": "Información y versionado de la API",
                    "responses": {"200": {"description": "Root con versión y endpoints"}},
                }
            },
            "/estadisticas": {
                "get": {
                    "tags": ["Ecosistema"],
                    "summary": "Estadísticas generales del ecosistema",
                    "responses": {"200": {"description": "Totales de participación"}},
                }
            },
            "/analitica": {
                "get": {
                    "tags": ["Ecosistema"],
                    "summary": "Analítica avanzada (nube, clusters, tendencias)",
                    "responses": {"200": {"description": "Reporte de analítica completo"}},
                }
            },
            "/participaciones": {
                "get": {
                    "tags": ["Datos"],
                    "security": [{"bearerAuth": []}],
                    "summary": "Listado paginado de participaciones ciudadanas",
                    "parameters": [
                        {"name": "page", "in": "query", "schema": {"type": "integer", "minimum": 1}},
                        {"name": "per_page", "in": "query", "schema": {"type": "integer", "maximum": 100}},
                        {"name": "sector", "in": "query", "schema": {"type": "string"}},
                        {"name": "departamento", "in": "query", "schema": {"type": "string"}},
                    ],
                    "responses": {
                        "200": {"description": "Página de participaciones"},
                        "401": {"description": "Token inválido o inactivo"},
                    },
                }
            },
            "/politicas": {
                "get": {
                    "tags": ["Datos"],
                    "summary": "Listado de políticas públicas activas",
                    "parameters": [
                        {"name": "sector", "in": "query", "schema": {"type": "integer"}, "description": "Filtrar por id de sector"},
                    ],
                    "responses": {"200": {"description": "Lista de políticas"}},
                }
            },
            "/politicas/{politica_id}": {
                "get": {
                    "tags": ["Datos"],
                    "summary": "Detalle de una política pública",
                    "parameters": [
                        {"name": "politica_id", "in": "path", "required": True, "schema": {"type": "integer"}},
                    ],
                    "responses": {
                        "200": {"description": "Política encontrada"},
                        "404": {"description": "Política no encontrada o inactiva"},
                    },
                }
            },
            "/sectores": {
                "get": {
                    "tags": ["Datos"],
                    "summary": "Sectores activos del catálogo",
                    "responses": {"200": {"description": "Lista de sectores"}},
                }
            },
            "/armonizacion": {
                "get": {
                    "tags": ["Ecosistema"],
                    "summary": "Matriz de armonización estratégica",
                    "responses": {"200": {"description": "Matriz con cobertura, gaps y ODS"}},
                }
            },
            "/clasificar": {
                "post": {
                    "tags": ["SRIE"],
                    "summary": "Clasificar un texto con el motor SRIE",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "justificacion": {"type": "string"},
                                        "propuesta": {"type": "string"},
                                        "problemas": {"type": "array", "items": {"type": "string"}},
                                    },
                                }
                            }
                        },
                    },
                    "responses": {
                        "200": {"description": "Clasificación top-3 con confianza"},
                        "400": {"description": "JSON requerido"},
                    },
                }
            },
            "/token": {
                "post": {
                    "tags": ["Tokens"],
                    "summary": "Generar token de acceso (requiere ADMIN_API_TOKEN en el header)",
                    "security": [{"adminToken": []}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "nombre": {"type": "string"},
                                        "role": {"type": "string", "enum": ["lectura", "escritura", "admin"]},
                                    },
                                    "required": ["nombre"],
                                }
                            }
                        },
                    },
                    "responses": {
                        "201": {"description": "Token creado"},
                        "400": {"description": "nombre requerido"},
                        "403": {"description": "ADMIN_API_TOKEN inválido"},
                    },
                }
            },
            "/openapi.json": {
                "get": {
                    "tags": ["Ecosistema"],
                    "summary": "Spec OpenAPI de esta API",
                    "responses": {"200": {"description": "Documento OpenAPI 3.0"}},
                }
            },
        },
        "components": {
            "securitySchemes": {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "description": "ApiToken generado en POST /api/v1/token",
                },
                "adminToken": {
                    "type": "http",
                    "scheme": "bearer",
                    "description": "ADMIN_API_TOKEN de configuración para emitir tokens",
                },
            }
        },
    }
