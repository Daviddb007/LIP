"""Tests del servicio de exportación CSV y su endpoint (app/services/export_service.py)."""
import csv
import io
import uuid

from app import db
from app.models.participacion import Participacion
from app.services.export_service import exportar_participaciones_csv


def _crear_participacion() -> Participacion:
    p = Participacion(
        departamento="Antioquia",
        municipio=f"Medellin-{uuid.uuid4().hex[:6]}",
        zona="urbana",
        justificacion="Falta agua potable en las veredas",
        propuesta="Construir acueductos veredales",
        rango_edad="26-35",
        genero="Masculino",
        ip_hash="hash-test",
        consentimiento_aceptado=True,
        consentimiento_version="2026-01",
    )
    db.session.add(p)
    db.session.commit()
    return p


class TestServicio:

    def test_exporta_csv_con_header(self, db):
        _crear_participacion()
        csv_str = exportar_participaciones_csv()
        assert csv_str.startswith("ID,")
        assert "Departamento" in csv_str

    def test_exporta_filas(self, db):
        p = _crear_participacion()
        csv_str = exportar_participaciones_csv()
        assert p.propuesta in csv_str
        assert p.departamento in csv_str

    def test_csv_parseable(self, db):
        _crear_participacion()
        csv_str = exportar_participaciones_csv()
        rows = list(csv.reader(io.StringIO(csv_str)))
        assert len(rows) >= 2
        assert len(rows[0]) == 12


class TestEndpoint:

    def test_export_requiere_login(self, client):
        r = client.get("/admin/export")
        assert r.status_code == 302

    def test_export_pagina_con_login(self, logged_in_client):
        r = logged_in_client.get("/admin/export")
        assert r.status_code == 200

    def test_export_csv_con_login(self, logged_in_client):
        r = logged_in_client.get("/admin/export/csv")
        assert r.status_code == 200
        assert "text/csv" in r.content_type
