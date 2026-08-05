"""Tests unitarios para validación de inputs v2."""
import pytest

from app.errors import ValidationError
from app.services.validation import validate_participacion, sanitize_text


class TestSanitizeText:

    def test_strips_html_tags(self):
        result = sanitize_text("<script>alert('x')</script>Hello")
        assert "<script>" not in result
        assert "Hello" in result

    def test_strips_nested_tags(self):
        result = sanitize_text("<b><i>Bold italic</i></b>")
        assert "<b>" not in result
        assert "Bold italic" in result

    def test_preserves_plain_text(self):
        result = sanitize_text("This is plain text")
        assert result == "This is plain text"

    def test_strips_event_handlers(self):
        result = sanitize_text('<div onmouseover="alert(1)">Text</div>')
        assert "<div" not in result

    def test_strips_images(self):
        result = sanitize_text('<img src="x" onerror="alert(1)">')
        assert "<img" not in result


class TestValidateUbicacion:

    def test_requiere_departamento(self):
        data = {"municipio": "Bogotá", "zona": "urbana", "problema_ids": [1],
                "justificacion": "Test", "propuesta": "Test", "actor_ids": [1],
                "beneficiario_ids": [1]}
        with pytest.raises(ValidationError, match="departamento es requerido"):
            validate_participacion(data)

    def test_departamento_invalido(self):
        data = {"departamento": "Atlantis", "municipio": "Ciudad", "zona": "urbana",
                "problema_ids": [1], "justificacion": "Test", "propuesta": "Test",
                "actor_ids": [1], "beneficiario_ids": [1]}
        with pytest.raises(ValidationError, match="Departamento inválido"):
            validate_participacion(data)

    def test_municipio_requerido(self):
        data = {"departamento": "Bogotá D.C.", "municipio": "", "zona": "urbana",
                "problema_ids": [1], "justificacion": "Test", "propuesta": "Test",
                "actor_ids": [1], "beneficiario_ids": [1]}
        with pytest.raises(ValidationError, match="municipio es requerido"):
            validate_participacion(data)

    def test_zona_invalida(self):
        data = {"departamento": "Bogotá D.C.", "municipio": "Bogotá", "zona": "costera",
                "problema_ids": [1], "justificacion": "Test", "propuesta": "Test",
                "actor_ids": [1], "beneficiario_ids": [1]}
        with pytest.raises(ValidationError, match="Zona inválida"):
            validate_participacion(data)


class TestValidateProblemas:

    def test_problema_requerido(self):
        data = {"departamento": "Bogotá D.C.", "municipio": "Bogotá", "zona": "urbana",
                "justificacion": "Test", "propuesta": "Test",
                "actor_ids": [1], "beneficiario_ids": [1]}
        with pytest.raises(ValidationError, match="seleccionar al menos un problema"):
            validate_participacion(data)

    def test_problema_max_3(self):
        data = {"departamento": "Bogotá D.C.", "municipio": "Bogotá", "zona": "urbana",
                "problema_ids": [1, 2, 3, 4], "justificacion": "Test", "propuesta": "Test",
                "actor_ids": [1], "beneficiario_ids": [1]}
        with pytest.raises(ValidationError, match="máximo 3 problemas"):
            validate_participacion(data)


class TestValidateTextos:

    def test_justificacion_requerida(self):
        data = {"departamento": "Bogotá D.C.", "municipio": "Bogotá", "zona": "urbana",
                "problema_ids": [1], "justificacion": "", "propuesta": "Test",
                "actor_ids": [1], "beneficiario_ids": [1]}
        with pytest.raises(ValidationError, match="justificación es requerida"):
            validate_participacion(data)

    def test_propuesta_requerida(self):
        data = {"departamento": "Bogotá D.C.", "municipio": "Bogotá", "zona": "urbana",
                "problema_ids": [1], "justificacion": "Test", "propuesta": "",
                "actor_ids": [1], "beneficiario_ids": [1]}
        with pytest.raises(ValidationError, match="propuesta es requerida"):
            validate_participacion(data)

    def test_justificacion_max_500(self):
        data = {"departamento": "Bogotá D.C.", "municipio": "Bogotá", "zona": "urbana",
                "problema_ids": [1], "justificacion": "x" * 501, "propuesta": "Test",
                "actor_ids": [1], "beneficiario_ids": [1]}
        with pytest.raises(ValidationError, match="máximo 500"):
            validate_participacion(data)

    def test_propuesta_max_500(self):
        data = {"departamento": "Bogotá D.C.", "municipio": "Bogotá", "zona": "urbana",
                "problema_ids": [1], "justificacion": "Test", "propuesta": "x" * 501,
                "actor_ids": [1], "beneficiario_ids": [1]}
        with pytest.raises(ValidationError, match="máximo 500"):
            validate_participacion(data)


class TestValidateGobernanza:

    def test_actor_requerido(self):
        data = {"departamento": "Bogotá D.C.", "municipio": "Bogotá", "zona": "urbana",
                "problema_ids": [1], "justificacion": "Test", "propuesta": "Test",
                "beneficiario_ids": [1]}
        with pytest.raises(ValidationError, match="seleccionar al menos un actor"):
            validate_participacion(data)

    def test_actor_max_3(self):
        data = {"departamento": "Bogotá D.C.", "municipio": "Bogotá", "zona": "urbana",
                "problema_ids": [1], "justificacion": "Test", "propuesta": "Test",
                "actor_ids": [1, 2, 3, 4], "beneficiario_ids": [1]}
        with pytest.raises(ValidationError, match="máximo 3 actores"):
            validate_participacion(data)

    def test_beneficiario_requerido(self):
        data = {"departamento": "Bogotá D.C.", "municipio": "Bogotá", "zona": "urbana",
                "problema_ids": [1], "justificacion": "Test", "propuesta": "Test",
                "actor_ids": [1]}
        with pytest.raises(ValidationError, match="seleccionar al menos un beneficiario"):
            validate_participacion(data)

    def test_beneficiario_max_5(self):
        data = {"departamento": "Bogotá D.C.", "municipio": "Bogotá", "zona": "urbana",
                "problema_ids": [1], "justificacion": "Test", "propuesta": "Test",
                "actor_ids": [1], "beneficiario_ids": [1, 2, 3, 4, 5, 6]}
        with pytest.raises(ValidationError, match="máximo 5 beneficiarios"):
            validate_participacion(data)


class TestSanitization:

    def test_sanitizes_text(self, app):
        with app.app_context():
            from app.models.catalog import ProblemaCatalogo, Actor, Beneficiario
            if ProblemaCatalogo.query.count() == 0:
                pytest.skip("No catalogs in DB")

            data = {"departamento": "Bogotá D.C.", "municipio": "Bogotá", "zona": "urbana",
                    "problema_ids": [ProblemaCatalogo.query.first().id],
                    "justificacion": "<script>alert(1)</script>Justificación",
                    "propuesta": "<b>Propuesta</b>",
                    "actor_ids": [Actor.query.first().id],
                    "beneficiario_ids": [Beneficiario.query.first().id]}
            result = validate_participacion(data)
            assert "<script>" not in result["justificacion"]
            assert "<b>" not in result["propuesta"]
