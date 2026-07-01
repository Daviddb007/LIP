from __future__ import annotations

from flask import Flask, jsonify, request
from flask_limiter.errors import RateLimitExceeded


class APIError(Exception):
    """Base API error with HTTP status code."""

    status_code: int = 500

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code

    def to_dict(self) -> dict[str, str]:
        return {'error': self.message}


class ValidationError(APIError):
    """Request data failed validation."""

    status_code = 400


class NotFoundError(APIError):
    """Requested resource does not exist."""

    status_code = 404


class RateLimitError(APIError):
    """Too many requests."""

    status_code = 429


class DatabaseError(APIError):
    """Database operation failed."""

    status_code = 500


def register_error_handlers(app: Flask) -> None:
    """Register centralized error handlers on the application."""

    @app.errorhandler(APIError)
    def handle_api_error(error: APIError):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    @app.errorhandler(RateLimitExceeded)
    def handle_rate_limit_exceeded(error: RateLimitExceeded):
        return jsonify({
            'error': 'Demasiadas solicitudes. Intenta de nuevo en un minuto.'
        }), 429

    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({'error': 'Recurso no encontrado'}), 404

    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        return jsonify({'error': 'Método no permitido'}), 405

    @app.errorhandler(500)
    def handle_internal_error(error):
        app.logger.error(f'Server error: {error}')
        return jsonify({'error': 'Error interno del servidor'}), 500

    @app.errorhandler(Exception)
    def handle_unexpected_exception(error: Exception):
        app.logger.exception('Unhandled exception occurred')
        return jsonify({'error': 'Ocurrió un error inesperado'}), 500
