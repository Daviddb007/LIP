from __future__ import annotations

import json

import pytest


class TestHealthCheck:
    """Tests for health check endpoint."""

    def test_health_returns_200(self, client):
        resp = client.get('/health')
        assert resp.status_code == 200

    def test_health_returns_healthy_status(self, client):
        resp = client.get('/health')
        data = resp.get_json()
        assert data['status'] == 'healthy'
        assert data['database'] == 'healthy'


class TestParticiparAPI:
    """Tests for participation submission API."""

    def test_sectores_returns_list(self, client):
        resp = client.get('/api/sectores')
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_sectores_have_required_fields(self, client):
        resp = client.get('/api/sectores')
        sector = resp.get_json()[0]
        assert 'id' in sector
        assert 'nombre' in sector
        assert 'icono' in sector

    def test_problemas_returns_list(self, client):
        resp = client.get('/api/problemas/1')
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)

    def test_enviar_requires_json(self, client):
        resp = client.post('/api/enviar')
        assert resp.status_code == 400

    def test_enviar_requires_sectores(self, client):
        resp = client.post('/api/enviar',
            data=json.dumps({'propuesta': 'Test'}),
            content_type='application/json')
        assert resp.status_code == 400

    def test_enviar_requires_propuesta(self, client):
        resp = client.post('/api/enviar',
            data=json.dumps({'sectores': [1]}),
            content_type='application/json')
        assert resp.status_code == 400

    def test_enviar_success(self, client):
        resp = client.post('/api/enviar',
            data=json.dumps({
                'sectores': [1],
                'propuesta': 'Test proposal for Colombia'
            }),
            content_type='application/json')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success'] is True
        assert 'id' in data

    def test_enviar_with_optional_fields(self, client):
        resp = client.post('/api/enviar',
            data=json.dumps({
                'sectores': [1, 2],
                'propuesta': 'Complete test proposal',
                'departamento': 'Antioquia',
                'municipio': 'Medellin',
                'rango_edad': '26-35',
                'genero': 'Masculino',
                'sector_prioritario_id': 1,
                'problema_principal': 'Desempleo'
            }),
            content_type='application/json')
        assert resp.status_code == 200

    def test_enviar_rate_limit(self, client):
        for _ in range(5):
            client.post('/api/enviar',
                data=json.dumps({'sectores': [1], 'propuesta': 'Test'}),
                content_type='application/json')

        resp = client.post('/api/enviar',
            data=json.dumps({'sectores': [1], 'propuesta': 'Rate limited'}),
            content_type='application/json')
        assert resp.status_code == 429


class TestResultadosAPI:
    """Tests for statistics/results API."""

    def test_estadisticas_returns_200(self, client):
        resp = client.get('/api/estadisticas')
        assert resp.status_code == 200

    def test_estadisticas_has_required_fields(self, client):
        resp = client.get('/api/estadisticas')
        data = resp.get_json()
        assert 'total_participaciones' in data
        assert 'total_departamentos' in data
        assert 'sectores' in data
        assert 'departamentos' in data


class TestAdminAuth:
    """Tests for admin authentication."""

    def test_login_page_renders(self, client):
        resp = client.get('/admin/login')
        assert resp.status_code == 200

    def test_login_page_has_csrf(self, client):
        resp = client.get('/admin/login')
        assert b'csrf_token' in resp.data

    def test_dashboard_requires_auth(self, client):
        resp = client.get('/admin/')
        assert resp.status_code == 302
        assert '/admin/login' in resp.headers['Location']

    def test_api_requires_auth(self, client):
        resp = client.get('/admin/api/participaciones')
        assert resp.status_code in (302, 401)

    def test_login_with_valid_csrf(self, client, app):
        with app.app_context():
            resp = client.get('/admin/login')
            html = resp.data.decode()

            import re
            match = re.search(r'name="csrf_token".*?value="([^"]+)"', html)
            assert match, 'CSRF token not found'

            csrf_token = match.group(1)
            resp = client.post('/admin/login', data={
                'csrf_token': csrf_token,
                'username': 'admin',
                'password': 'admin'
            }, follow_redirects=False)
            assert resp.status_code == 302

    def test_login_with_wrong_password(self, client, app):
        with app.app_context():
            resp = client.get('/admin/login')
            html = resp.data.decode()

            import re
            match = re.search(r'name="csrf_token".*?value="([^"]+)"', html)
            csrf_token = match.group(1)

            resp = client.post('/admin/login', data={
                'csrf_token': csrf_token,
                'username': 'admin',
                'password': 'wrongpassword'
            })
            assert resp.status_code == 200
            assert b'Credenciales inv' in resp.data


class TestAdminExport:
    """Tests for CSV export."""

    def test_export_requires_auth(self, client):
        resp = client.get('/admin/api/exportar')
        assert resp.status_code == 302

    def test_export_returns_csv(self, logged_in_client):
        resp = logged_in_client.get('/admin/api/exportar')
        assert resp.status_code == 200
        assert resp.content_type == 'text/csv'
