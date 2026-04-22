# tests/test_app_routes.py
"""
Tests de integración para las rutas Flask de app.py.
Usa una instancia de la app con OdooManager y AnalyticsDB mockeados.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta


# ---------------------------------------------------------------------------
# Rutas públicas (sin sesión requerida)
# ---------------------------------------------------------------------------

class TestLoginPage:
    """Tests para la página de login."""

    def test_login_page_returns_200(self, client):
        response = client.get('/login')
        assert response.status_code == 200

    def test_login_page_contains_html(self, client):
        response = client.get('/login')
        assert b'html' in response.data.lower()


# ---------------------------------------------------------------------------
# Redirecciones cuando no hay sesión activa
# ---------------------------------------------------------------------------

class TestUnauthenticatedRedirects:
    """Tests que verifican la redirección al login cuando no hay sesión."""

    @pytest.mark.parametrize("url", [
        '/inventory',
        '/dashboard',
        '/exportacion',
        '/analytics',
        '/export/excel',
        '/export/excel/exportacion',
    ])
    def test_protected_route_redirects_to_login(self, client, url):
        response = client.get(url)
        assert response.status_code in (302, 308)
        assert '/login' in response.headers.get('Location', '')

    def test_root_redirects(self, client):
        """La raíz / debe redirigir si no hay sesión (o retornar 200/302)."""
        response = client.get('/')
        assert response.status_code in (200, 302, 308, 404)


# ---------------------------------------------------------------------------
# Logout
# ---------------------------------------------------------------------------

class TestLogout:
    """Tests para cerrar sesión."""

    def test_logout_redirects_to_login(self, client, authenticated_session):
        response = authenticated_session.get('/logout')
        assert response.status_code in (302, 308)
        assert '/login' in response.headers.get('Location', '')

    def test_logout_clears_session(self, client, authenticated_session):
        authenticated_session.get('/logout')
        # Después del logout, /inventory debe redirigir de nuevo al login
        response = authenticated_session.get('/inventory')
        assert response.status_code in (302, 308)
        assert '/login' in response.headers.get('Location', '')


# ---------------------------------------------------------------------------
# Rutas autenticadas básicas
# ---------------------------------------------------------------------------

class TestAuthenticatedRoutes:
    """Tests para rutas que requieren sesión activa."""

    def test_inventory_returns_200_with_session(self, authenticated_session):
        response = authenticated_session.get('/inventory')
        assert response.status_code == 200

    def test_dashboard_returns_200_with_session(self, authenticated_session):
        response = authenticated_session.get('/dashboard')
        assert response.status_code == 200

    def test_exportacion_returns_200_with_session(self, authenticated_session):
        response = authenticated_session.get('/exportacion')
        assert response.status_code == 200

    def test_analytics_returns_200_with_session(self, authenticated_session):
        response = authenticated_session.get('/analytics')
        assert response.status_code == 200


# ---------------------------------------------------------------------------
# Security headers
# ---------------------------------------------------------------------------

class TestSecurityHeaders:
    """Tests para verificar la presencia de headers de seguridad OWASP."""

    def test_x_content_type_options_header(self, client):
        response = client.get('/login')
        assert response.headers.get('X-Content-Type-Options') == 'nosniff'

    def test_x_frame_options_header(self, client):
        response = client.get('/login')
        assert response.headers.get('X-Frame-Options') == 'DENY'

    def test_x_xss_protection_header(self, client):
        response = client.get('/login')
        assert response.headers.get('X-XSS-Protection') == '1; mode=block'

    def test_referrer_policy_header(self, client):
        response = client.get('/login')
        assert response.headers.get('Referrer-Policy') == 'strict-origin-when-cross-origin'

    def test_permissions_policy_header(self, client):
        response = client.get('/login')
        pp = response.headers.get('Permissions-Policy', '')
        assert 'geolocation' in pp


# ---------------------------------------------------------------------------
# Session fingerprint (session hijacking detection)
# ---------------------------------------------------------------------------

class TestSessionFingerprint:
    """Tests para la detección de secuestro de sesión."""

    def test_fingerprint_mismatch_redirects_to_login(self, app):
        """
        Si el User-Agent cambia entre requests (distintos IPs o UA),
        el fingerprint no coincide y la sesión debe invalidarse.
        """
        with app.test_client() as test_client:
            # Establecer sesión con fingerprint de UA original
            original_ua = 'Mozilla/5.0 (Windows NT 10.0)'
            original_ip = '127.0.0.1'

            # Primer request: autenticar y almacenar fingerprint
            with test_client.session_transaction() as sess:
                sess['username'] = 'test@example.com'
                sess['last_activity'] = datetime.now().isoformat()
                import hashlib
                original_fp = hashlib.sha256(
                    f"{original_ua}{original_ip}".encode()
                ).hexdigest()
                sess['_security_fingerprint'] = original_fp

            # Segundo request con UA diferente — simula hijacking
            different_ua = 'EvilBot/1.0'
            response = test_client.get(
                '/inventory',
                headers={'User-Agent': different_ua}
            )
            # Debe redirigir al login por fingerprint mismatch
            assert response.status_code in (302, 308)
            location = response.headers.get('Location', '')
            assert '/login' in location


# ---------------------------------------------------------------------------
# Session expiry
# ---------------------------------------------------------------------------

class TestSessionExpiry:
    """Tests para la expiración de sesión por inactividad."""

    def test_expired_session_redirects_to_login(self, app):
        """Una sesión con last_activity muy antigua debe expirar."""
        with app.test_client() as test_client:
            old_time = (datetime.now() - timedelta(hours=2)).isoformat()
            with test_client.session_transaction() as sess:
                sess['username'] = 'test@example.com'
                sess['last_activity'] = old_time

            response = test_client.get('/inventory')
            assert response.status_code in (302, 308)
            assert '/login' in response.headers.get('Location', '')


# ---------------------------------------------------------------------------
# Inventory POST filters
# ---------------------------------------------------------------------------

class TestInventoryPost:
    """Tests para el POST del inventario con filtros."""

    def test_inventory_post_with_filters_returns_200(self, authenticated_session):
        response = authenticated_session.post('/inventory', data={
            'search_term': 'amoxicilina',
            'category_id': '1',
            'line_id': '10',
        })
        assert response.status_code == 200

    def test_inventory_post_empty_filters_returns_200(self, authenticated_session):
        response = authenticated_session.post('/inventory', data={})
        assert response.status_code == 200


# ---------------------------------------------------------------------------
# Dashboard POST filters
# ---------------------------------------------------------------------------

class TestDashboardPost:
    """Tests para el POST del dashboard con filtros (debe redirigir a GET)."""

    def test_dashboard_post_redirects_to_get(self, authenticated_session):
        response = authenticated_session.post('/dashboard', data={
            'category_id': '1',
            'line_id': '10',
        })
        # POST en dashboard redirige a GET con params
        assert response.status_code in (302, 308)


# ---------------------------------------------------------------------------
# Export endpoints (sesión requerida)
# ---------------------------------------------------------------------------

class TestExportEndpoints:
    """Tests para los endpoints de exportación."""

    def test_export_excel_with_session(self, authenticated_session):
        response = authenticated_session.get('/export/excel')
        # Puede ser 200 (Excel) o 302 (sin datos → redirect a exportacion)
        assert response.status_code in (200, 302, 308)

    def test_export_excel_exportacion_with_session(self, authenticated_session):
        response = authenticated_session.get('/export/excel/exportacion')
        assert response.status_code in (200, 302, 308)
