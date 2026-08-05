"""Jerarquía de errores API y handlers registrados en la app factory.

Todos los errores heredan de APIError, que a su vez hereda de Flask HTTPException.
Los handlers se registran con app.register_error_handler() en _register_error_handlers().
"""
from __future__ import annotations

from flask import Flask, jsonify


class APIError(Exception):
    """Excepción base para errores de API."""

    status_code: int = 500
    message: str = "Error interno del servidor"

    def __init__(self, message: str | None = None, status_code: int | None = None):
        self.message = message or self.__class__.message
        self.status_code = status_code or self.__class__.status_code
        super().__init__(self.message)

    def to_dict(self) -> dict:
        return {"error": self.message}


class ValidationError(APIError):
    """Datos de entrada inválidos."""

    status_code = 400
    message = "Datos de entrada inválidos"


class NotFoundError(APIError):
    """Recurso no encontrado."""

    status_code = 404
    message = "Recurso no encontrado"


class RateLimitError(APIError):
    """Demasiadas solicitudes."""

    status_code = 429
    message = "Demasiadas solicitudes. Intenta de nuevo en un minuto."


class DatabaseError(APIError):
    """Error al interactuar con la base de datos."""

    status_code = 500
    message = "Error al procesar la solicitud"


class UnauthorizedError(APIError):
    """No autenticado."""

    status_code = 401
    message = "No autenticado"


class ForbiddenError(APIError):
    """No autorizado."""

    status_code = 403
    message = "No autorizado"


def register_error_handlers(app: Flask) -> None:
    """Registra handlers para errores personalizados y nativos de Flask."""

    @app.errorhandler(APIError)
    def handle_api_error(error: APIError):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({"error": "Recurso no encontrado"}), 404

    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        return jsonify({"error": "Método no permitido"}), 405

    @app.errorhandler(429)
    def handle_rate_limit(error):
        return jsonify({"error": "Demasiadas solicitudes. Intenta de nuevo en un minuto."}), 429

    @app.errorhandler(500)
    def handle_internal_error(error):
        return jsonify({"error": "Error interno del servidor"}), 500

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        from flask_limiter.errors import RateLimitExceeded
        if isinstance(error, RateLimitExceeded):
            return jsonify({"error": "Demasiadas solicitudes. Intenta de nuevo en un minuto."}), 429
        app.logger.exception("Error inesperado: %s", error)
        return jsonify({"error": "Ocurrió un error inesperado"}), 500
