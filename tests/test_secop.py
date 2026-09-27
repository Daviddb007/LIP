"""Tests del visor SECOP II público y del servicio de licitación (/secop)."""
from __future__ import annotations

from datetime import date

import pytest

from app import cache
from app.models.secop import LeadSecop, SecopCorte, SecopProceso
from app.services import secop_service

CORTE = date(2026, 9, 26)

RAW_SAMPLE = [
    {
        "entidad": "EDENORTE",
        "departamento_entidad": "Antioquia",
        "ciudad_entidad": "Yarumal",
        "nombre_del_procedimiento": "CONSTRUCCIÓN DE LA CIUDADELA EDUCATIVA ÁGORA",
        "modalidad_de_contratacion": "Contratación Directa (con ofertas)",
        "tipo_de_contrato": "Obra",
        "precio_base": "14363770347",
        "fecha_de_recepcion_de": "2026-09-30T00:00:00.000",
        "urlproceso": {
            "url": "https://community.secop.gov.co/Public/Tendering/OpportunityDetail/Index?noticeUID=CO1.NTC.10912268"
        },
    },
    {
        "entidad": "ALCALDIA MUNICIPAL DE ZIPAQUIRA",
        "departamento_entidad": "Cundinamarca",
        "ciudad_entidad": "Zipaquira",
        "nombre_del_procedimiento": "SUMINISTRO DE PAPELERIA Y TONER",
        "modalidad_de_contratacion": "Mínima cuantía",
        "tipo_de_contrato": "",
        "precio_base": "4500000",
        "fecha_de_recepcion_de": "2026-10-05T00:00:00.000",
        "urlproceso": {
            "url": "https://community.secop.gov.co/Public/Tendering/OpportunityDetail/Index?noticeUID=CO1.NTC.99999999"
        },
    },
]


@pytest.fixture
def clean_secop(db):
    """Limpia tablas SECOP (los commits persisten entre tests en esta suite)."""
    SecopProceso.query.delete()
    SecopCorte.query.delete()
    db.session.commit()
    return db


@pytest.fixture
def secop_data(clean_secop):
    db = clean_secop
    db.session.add(SecopCorte(corte=CORTE, total=2))
    db.session.add(SecopProceso(
        entidad="EDENORTE",
        departamento="Antioquia",
        ciudad="Yarumal",
        nombre="CONSTRUCCIÓN DE LA CIUDADELA EDUCATIVA ÁGORA",
        modalidad="Contratación Directa (con ofertas)",
        tipo_contrato="Obra",
        valor=14363770347,
        requiere_rup=True,
        fecha_limite=date(2026, 9, 30),
        corte=CORTE,
        temas=["Infraestructura / Obra pública"],
        pilares=["educacion"],
        url="https://community.secop.gov.co/Public/Tendering/OpportunityDetail/Index?noticeUID=CO1.NTC.10912268",
    ))
    db.session.add(SecopProceso(
        entidad="ALCALDIA MUNICIPAL DE ZIPAQUIRA",
        departamento="Cundinamarca",
        ciudad="Zipaquira",
        nombre="SUMINISTRO DE PAPELERIA Y TONER",
        modalidad="Mínima cuantía",
        tipo_contrato="Compraventa",
        valor=4500000,
        requiere_rup=False,
        fecha_limite=date(2026, 10, 5),
        corte=CORTE,
        temas=[],
        pilares=[],
        url="https://community.secop.gov.co/Public/Tendering/OpportunityDetail/Index?noticeUID=CO1.NTC.99999999",
    ))
    db.session.commit()
    cache.clear()
    return db


@pytest.fixture
def clean_leads(db):
    LeadSecop.query.delete()
    db.session.commit()
    return db


# ---------------------------------------------------------------- servicio

def test_normalizar_registros():
    records = secop_service._normalizar_registros(RAW_SAMPLE, CORTE)
    assert len(records) == 2
    primera = records[0]
    assert primera["e"] == "EDENORTE"
    assert primera["d"] == "Antioquia"
    assert primera["v"] == 14363770347
    assert primera["rup"] is True
    assert primera["dl"] == 4  # 30 sep - 26 sep
    assert primera["f"] == "2026-09-30"
    assert secop_service.URL_OK.match(primera["u"])
    assert primera["tm"]  # detección de temas no vacía


def test_minima_cuantia_no_exige_rup():
    records = secop_service._normalizar_registros(RAW_SAMPLE, CORTE)
    zipaquira = records[1]
    assert zipaquira["rup"] is False
    assert zipaquira["t"] == "No Especificado"


def test_validar_ok_y_errores():
    ok = secop_service._normalizar_registros(RAW_SAMPLE, CORTE)
    assert secop_service.validar(ok) == []
    malo = [{"e": "", "d": "X", "c": "X", "n": "X", "m": "X", "t": "X", "v": -1, "rup": "si", "dl": -2, "f": "26/09", "u": "https://mal", "tm": "no-es-lista"}]
    errores = secop_service.validar(malo)
    assert len(errores) >= 6


def test_filtra_fechas_anteriores_al_corte():
    raw = list(RAW_SAMPLE)
    raw.append(dict(raw[0], fecha_de_recepcion_de="2026-09-20T00:00:00.000"))
    records = secop_service._normalizar_registros(raw, CORTE)
    assert len(records) == 2


def test_actualizar_secop_persiste(monkeypatch, clean_secop, app):
    monkeypatch.setattr(secop_service, "_fetch_paginated", lambda params: RAW_SAMPLE)
    res = secop_service.actualizar_secop(CORTE)
    assert res["total"] == 2
    assert res["corte"] == "2026-09-26"
    assert SecopCorte.query.filter_by(corte=CORTE).first().total == 2
    assert SecopProceso.query.filter_by(corte=CORTE).count() == 2


def test_actualizar_secop_valida_antes_de_publicar(monkeypatch, clean_secop, app):
    basura = [{
        "entidad": "",
        "departamento_entidad": "Bogotá",
        "ciudad_entidad": "Bogotá",
        "nombre_del_procedimiento": "ALGO",
        "modalidad_de_contratacion": "Licitación pública",
        "tipo_de_contrato": "Servicios",
        "precio_base": "1000",
        "fecha_de_recepcion_de": "2026-10-01T00:00:00.000",
        "urlproceso": {"url": "https://community.secop.gov.co/Public/Tendering/OpportunityDetail/Index?noticeUID=CO1.NTC.12345"},
    }]
    monkeypatch.setattr(secop_service, "_fetch_paginated", lambda params: basura)
    with pytest.raises(secop_service.SecopError):
        secop_service.actualizar_secop(CORTE)
    assert SecopProceso.query.filter_by(corte=CORTE).count() == 0


# ---------------------------------------------------------------- rutas

def test_secop_vacio_sin_datos(clean_secop, client):
    cache.clear()
    r = client.get("/secop")
    assert r.status_code == 200
    assert "Aún no hay datos de SECOP" in r.get_data(as_text=True)


def test_secop_con_datos(secop_data, client):
    r = client.get("/secop")
    body = r.get_data(as_text=True)
    assert r.status_code == 200
    assert "Oportunidades de contratación pública" in body
    assert "EDENORTE" in body
    assert "procesos vigentes" in body


def test_secop_filtros(secop_data, client):
    cache.clear()
    r = client.get("/secop?q=papeleria&rup=0")
    body = r.get_data(as_text=True)
    assert r.status_code == 200
    assert "PAPELERIA" in body
    assert "EDENORTE" not in body


def test_secop_filtro_pilar(secop_data, client):
    cache.clear()
    r = client.get("/secop?pilar=educacion")
    body = r.get_data(as_text=True)
    assert r.status_code == 200
    assert "EDENORTE" in body
    assert "ZIPAQUIRA" not in body


def test_secop_api_datos(secop_data, client):
    cache.clear()
    r = client.get("/secop/api/datos")
    assert r.status_code == 200
    data = r.get_json()
    assert data["total"] == 2
    assert any(d["label"] == "Antioquia" for d in data["departamentos"])


def test_secop_licitar_get(client):
    r = client.get("/secop/licitar")
    assert r.status_code == 200
    body = r.get_data(as_text=True)
    assert "empezar a licitar en lo público" in body
    assert "profesionales" in body


def test_secop_lead_valido(clean_leads, client):
    r = client.post("/secop/licitar", data={
        "nombre": "María López",
        "empresa": "Constructora Andina SAS",
        "email": "maria@constructora.co",
        "telefono": "3001234567",
        "sector": "Construcción",
        "estado_rup": "No, necesito ayuda con el RUP",
        "mensaje": "Queremos licitar obras viales",
    }, follow_redirects=True)
    assert r.status_code == 200
    lead = LeadSecop.query.filter_by(email="maria@constructora.co").first()
    assert lead is not None
    assert lead.nombre == "María López"
    assert lead.empresa == "Constructora Andina SAS"
    assert lead.estado_rup == "No, necesito ayuda con el RUP"
    assert "te contactará" in r.get_data(as_text=True)


def test_secop_lead_sanitiza_html(clean_leads, client):
    r = client.post("/secop/licitar", data={
        "nombre": "<script>alert(1)</script>Carlos",
        "empresa": "Tecnologías Beta",
        "email": "carlos@beta.co",
        "telefono": "3110000000",
        "mensaje": "<b>Hola</b>",
    }, follow_redirects=True)
    assert r.status_code == 200
    lead = LeadSecop.query.filter_by(email="carlos@beta.co").first()
    assert lead is not None
    assert "<script>" not in lead.nombre
    assert "<b>" not in lead.mensaje
    assert "Carlos" in lead.nombre


def test_secop_lead_invalido(clean_leads, client):
    r = client.post("/secop/licitar", data={
        "nombre": "",
        "empresa": "X",
        "email": "correo-malo",
        "telefono": "",
    })
    assert r.status_code == 400
    assert LeadSecop.query.filter_by(email="correo-malo").first() is None


# ---------------------------------------------------------------- SEO/GEO

def test_sitemap_incluye_secop(client):
    r = client.get("/sitemap.xml")
    assert r.status_code == 200
    body = r.get_data(as_text=True)
    assert "/secop" in body
    assert "/secop/licitar" in body
    assert "sitemaps.org" in body


def test_robots_txt(client):
    r = client.get("/robots.txt")
    assert r.status_code == 200
    body = r.get_data(as_text=True)
    assert "Sitemap:" in body
    assert "User-agent:" in body


def test_llms_txt(client):
    r = client.get("/llms.txt")
    assert r.status_code == 200
    body = r.get_data(as_text=True)
    assert "SECOP" in body
    assert "/secop/licitar" in body
