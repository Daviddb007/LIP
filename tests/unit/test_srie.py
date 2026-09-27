"""Tests unitarios para el motor SRIE v2."""

from app.services.srie.matcher import clasificar_texto, get_pilar_by_slug
from app.services.srie.confidence import calcular_confianza
from app.services.srie.explanation import generar_explicacion


class TestMatcher:

    def test_seguridad_matches_seguridad_pilar(self, app):
        with app.app_context():
            results = clasificar_texto("La inseguridad en mi barrio es terrible, nos roban constantly")
            assert len(results) > 0
            pilar_slugs = [r["pilar_slug"] for r in results]
            assert "seguridad" in pilar_slugs

    def test_educacion_matches_educacion_pilar(self, app):
        with app.app_context():
            results = clasificar_texto("La educación en Colombia es deficiente, los colegios están deteriorados")
            pilar_slugs = [r["pilar_slug"] for r in results]
            assert "educacion" in pilar_slugs

    def test_salud_matches_salud_pilar(self, app):
        with app.app_context():
            results = clasificar_texto("El sistema de salud está colapsado, hay listas de espera enormes")
            pilar_slugs = [r["pilar_slug"] for r in results]
            assert "recuperar-la-salud" in pilar_slugs

    def test_campo_matches_campo_pilar(self, app):
        with app.app_context():
            results = clasificar_texto("Los campesinos no tienen tierra, la agricultura está abandonada")
            pilar_slugs = [r["pilar_slug"] for r in results]
            assert "campo-y-el-agro" in pilar_slugs

    def test_corrupcion_matches_corrupcion_pilar(self, app):
        with app.app_context():
            results = clasificar_texto("La corrupción es endémica, los contratos públicos son fraudulentos")
            pilar_slugs = [r["pilar_slug"] for r in results]
            assert "erradicar-la-corrupcion" in pilar_slugs

    def test_returns_top_3(self, app):
        with app.app_context():
            results = clasificar_texto("Seguridad y educación son importantes para la juventud")
            assert len(results) <= 3

    def test_returns_score_between_0_and_1(self, app):
        with app.app_context():
            results = clasificar_texto("Test text")
            for r in results:
                assert 0.0 <= r["score"] <= 1.0

    def test_sector_boost(self, app):
        with app.app_context():
            results = clasificar_texto("Empleo y trabajo formal", sector_slug="empleo-economia")
            assert len(results) > 0

    def test_problema_direct_boost(self, app):
        with app.app_context():
            results = clasificar_texto("Inseguridad barrial", problema_slug="inseguridad-barrios")
            assert len(results) > 0

    def test_get_pilar_by_slug(self, app):
        with app.app_context():
            pilar = get_pilar_by_slug("seguridad")
            assert pilar is not None
            assert "Seguridad" in pilar.nombre

    def test_get_pilar_by_slug_not_found(self, app):
        with app.app_context():
            pilar = get_pilar_by_slug("nonexistent-slug")
            assert pilar is None


class TestConfidence:

    def test_high_score_high_confidence(self, app):
        conf = calcular_confianza(
            score=0.9, justificacion="Texto largo con detalles",
            propuesta="Propuesta concreta con implementación",
            keywords_encontradas=["seguridad", "inseguridad", "robo"],
            tiene_problema_directo=True,
        )
        assert conf >= 0.80

    def test_low_score_low_confidence(self, app):
        conf = calcular_confianza(
            score=0.1, justificacion="X",
            propuesta="Y",
            keywords_encontradas=["uno"],
            tiene_problema_directo=False,
        )
        assert conf < 0.50

    def test_long_text_bonus(self, app):
        short = calcular_confianza(0.5, "Corto", "Corto", ["kw"], True)
        long = calcular_confianza(0.5, "x" * 150, "y" * 150, ["kw"], True)
        assert long >= short

    def test_problem_direct_bonus(self, app):
        with_direct = calcular_confianza(0.5, "Test", "Test", ["kw"], True)
        without_direct = calcular_confianza(0.5, "Test", "Test", ["kw"], False)
        assert with_direct >= without_direct

    def test_confidence_range(self, app):
        conf = calcular_confianza(0.5, "Test", "Test", ["kw"], False)
        assert 0.0 <= conf <= 1.0

    def test_single_keyword_penalty(self, app):
        with_many = calcular_confianza(0.5, "Test", "Test", ["kw1", "kw2", "kw3"], False)
        with_one = calcular_confianza(0.5, "Test", "Test", ["kw1"], False)
        assert with_many >= with_one


class TestExplanation:

    def test_high_confidence_first_rank(self, app):
        exp = generar_explicacion("Seguridad", 0.95, ["seguridad", "robo"], 1)
        assert "Seguridad" in exp
        assert "directamente" in exp

    def test_medium_confidence_first_rank(self, app):
        exp = generar_explicacion("Seguridad", 0.65, ["seguridad"], 1)
        assert "relaciona" in exp

    def test_low_confidence_first_rank(self, app):
        exp = generar_explicacion("Seguridad", 0.30, [], 1)
        assert "provisionalmente" in exp

    def test_second_rank_high(self, app):
        exp = generar_explicacion("Educación", 0.70, ["colegio"], 2)
        assert "también" in exp

    def test_second_rank_low(self, app):
        exp = generar_explicacion("Educación", 0.30, [], 2)
        assert "parcial" in exp
