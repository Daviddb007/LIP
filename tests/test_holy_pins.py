"""Tests v2 — PINs de LIP validados contra el loader REAL MultiProjectConfig.

Copia del estándar de Stonelytics: falla si governance queda vacío (el bug
que la v1 manual ocultaba) y valida pines/rules contra la config canónica.
"""
from __future__ import annotations

from pathlib import Path

from holy_core.runtime.continuous.project_config import MultiProjectConfig


class TestHolyPins:
    """Verifica que los PINs del proyecto pasan por el loader real."""

    ROOT = Path(__file__).resolve().parent.parent
    CONFIG_PATH = ROOT / "holy_projects.yaml"

    def _config(self):
        configs = MultiProjectConfig(config_path=self.CONFIG_PATH).load()
        assert len(configs) == 1, f"Esperado 1 proyecto, cargados {len(configs)}"
        return configs[0]

    def _governance(self):
        cfg = self._config()
        gov = cfg.governance
        assert gov, "governance vacío — MultiProjectConfig no normalizó la config"
        return gov

    def _pines(self):
        return self._governance().get("pines", [])

    def _rules(self):
        return self._governance().get("classification_rules", [])

    def test_loader_real_ve_gobernanza(self):
        """Regresión: el loader real debe capturar pines y rules."""
        gov = self._governance()
        assert len(gov.get("pines", [])) > 0, "MultiProjectConfig no cargó pines"
        assert len(gov.get("classification_rules", [])) > 0, \
            "MultiProjectConfig no cargó classification_rules"

    def test_config_canonica_nested(self):
        """La config debe ser canónica: governance bajo projects[0]."""
        cfg = self._config()
        assert cfg.nombre == "lip"
        assert cfg.root.resolve() == self.ROOT.resolve()

    def test_comando_tests_usa_venv(self):
        """LIP solo corre con su venv (flask_caching falta en el Python de sistema)."""
        assert "venv/Scripts/python.exe" in self._config().comando_tests

    def test_pines_tienen_codigo_unico(self):
        pines = self._pines()
        codigos = [p["codigo"] for p in pines]
        duplicados = set(c for c in codigos if codigos.count(c) > 1)
        assert not duplicados, f"PINs duplicados: {duplicados}"

    def test_pines_tienen_severidad_valida(self):
        pines = self._pines()
        validas = {"critico", "alto", "medio"}
        for p in pines:
            assert p.get("severity", "").lower() in validas, \
                f"PIN {p['codigo']}: severidad '{p.get('severity')}' inválida"

    def test_pines_tienen_area_definida(self):
        for p in self._pines():
            assert "area" in p and p["area"], f"PIN {p['codigo']}: sin área definida"

    def test_pines_tienen_regla_definida(self):
        for p in self._pines():
            assert "regla" in p and p["regla"], f"PIN {p['codigo']}: sin regla definida"

    def test_pin_P01_protege_modelos(self):
        """P-01 debe proteger app/models/ con severidad CRITICO."""
        pines = self._pines()
        p01 = next((p for p in pines if p["codigo"] == "P-01"), None)
        assert p01 is not None, "P-01 no encontrado"
        assert "app/models" in p01.get("area", ""), "P-01 debe proteger app/models/"
        assert p01.get("severity", "").lower() == "critico", "P-01 debe ser CRITICO"

    def test_pin_P03_protege_app_factory(self):
        """P-03 debe proteger app/__init__.py con severidad CRITICO."""
        pines = self._pines()
        p03 = next((p for p in pines if p["codigo"] == "P-03"), None)
        assert p03 is not None, "P-03 no encontrado"
        assert "__init__" in p03.get("area", ""), "P-03 debe proteger app/__init__.py"
        assert p03.get("severity", "").lower() == "critico", "P-03 debe ser CRITICO"

    def test_fundacionales_tienen_ruta_en_classification_rules(self):
        """Cada PIN CRITICO debe tener una classification rule FUNDACIONAL para su ruta."""
        pines = [p for p in self._pines() if p.get("severity", "").lower() == "critico"]
        rules = self._rules()
        rule_patterns = [r["patron"] for r in rules if r.get("categoria", "").lower() == "fundacional"]

        for pin in pines:
            area = pin.get("area", "")
            matched = any(
                area.startswith(p.replace("*", "").rstrip("/"))
                for p in rule_patterns
            )
            assert matched, f"PIN {pin['codigo']} ({area}): sin classification rule FUNDACIONAL"

    def test_hay_al_menos_un_pin_bloqueante(self):
        """Debe haber al menos un PIN que bloquee el pipeline (CRITICO o ALTO)."""
        pines = self._pines()
        bloqueantes = [p for p in pines if p.get("severity", "").lower() in ("critico", "alto")]
        assert len(bloqueantes) > 0, "No hay PINs bloqueantes"

    def test_no_hay_approved_bugs_hardcoded(self):
        """Verifica que holy_runner.py no contenga approved_bugs hardcoded."""
        runner_path = self.ROOT / "holy_runner.py"
        content = runner_path.read_text(encoding="utf-8")
        assert "approved_bugs" not in content, \
            "holy_runner.py contiene approved_bugs hardcoded — eliminar!"

    def test_runner_usa_holy_core(self):
        """El runner debe delegar en holy-core, no en lógica propia."""
        runner_path = self.ROOT / "holy_runner.py"
        content = runner_path.read_text(encoding="utf-8")
        assert "holy_core" in content, "holy_runner.py no importa holy_core"
