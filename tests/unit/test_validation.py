from __future__ import annotations

import pytest

from app.services.validation import (
    validate_participacion,
    DEPARTAMENTOS_COL,
    VALID_RANGOS_EDAD,
    VALID_GENEROS,
)
from app.errors import ValidationError


class TestValidateSectores:
    """Tests for sector validation."""

    def test_valid_single_sector(self):
        validate_participacion({'sectores': [1], 'propuesta': 'Test proposal'})

    def test_valid_multiple_sectors(self):
        validate_participacion({'sectores': [1, 2, 3], 'propuesta': 'Test proposal'})

    def test_empty_sectors_raises(self):
        with pytest.raises(ValidationError, match='sector'):
            validate_participacion({'sectores': [], 'propuesta': 'Test'})

    def test_missing_sectors_raises(self):
        with pytest.raises(ValidationError, match='sector'):
            validate_participacion({'propuesta': 'Test'})

    def test_too_many_sectors_raises(self):
        with pytest.raises(ValidationError, match='máximo'):
            validate_participacion({'sectores': [1, 2, 3, 4], 'propuesta': 'Test'})

    def test_non_integer_sector_ids_raises(self):
        with pytest.raises(ValidationError, match='inválidos'):
            validate_participacion({'sectores': ['a', 'b'], 'propuesta': 'Test'})


class TestValidatePropuesta:
    """Tests for proposal validation."""

    def test_valid_propuesta(self):
        validate_participacion({'sectores': [1], 'propuesta': 'My proposal'})

    def test_empty_propuesta_raises(self):
        with pytest.raises(ValidationError, match='propuesta'):
            validate_participacion({'sectores': [1], 'propuesta': ''})

    def test_whitespace_only_propuesta_raises(self):
        with pytest.raises(ValidationError, match='propuesta'):
            validate_participacion({'sectores': [1], 'propuesta': '   '})

    def test_too_long_propuesta_raises(self):
        with pytest.raises(ValidationError, match='500'):
            validate_participacion({'sectores': [1], 'propuesta': 'x' * 501})


class TestValidateOptionalFields:
    """Tests for optional field validation."""

    def test_valid_departamento(self):
        validate_participacion({
            'sectores': [1], 'propuesta': 'Test',
            'departamento': 'Antioquia'
        })

    def test_invalid_departamento_raises(self):
        with pytest.raises(ValidationError, match='Departamento'):
            validate_participacion({
                'sectores': [1], 'propuesta': 'Test',
                'departamento': 'InvalidDept'
            })

    def test_valid_rango_edad(self):
        validate_participacion({
            'sectores': [1], 'propuesta': 'Test',
            'rango_edad': '26-35'
        })

    def test_invalid_rango_edad_raises(self):
        with pytest.raises(ValidationError, match='edad'):
            validate_participacion({
                'sectores': [1], 'propuesta': 'Test',
                'rango_edad': '100-200'
            })

    def test_valid_genero(self):
        validate_participacion({
            'sectores': [1], 'propuesta': 'Test',
            'genero': 'Masculino'
        })

    def test_invalid_genero_raises(self):
        with pytest.raises(ValidationError, match='Género'):
            validate_participacion({
                'sectores': [1], 'propuesta': 'Test',
                'genero': 'InvalidGender'
            })

    def test_empty_optional_fields_accepted(self):
        validate_participacion({
            'sectores': [1], 'propuesta': 'Test',
            'departamento': '', 'rango_edad': '', 'genero': ''
        })
