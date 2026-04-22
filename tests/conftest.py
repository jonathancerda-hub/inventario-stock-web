# tests/conftest.py
"""
Fixtures compartidas para todos los tests.
Proporciona app Flask configurada para testing, cliente HTTP y mocks de servicios externos.
"""

import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_odoo_manager():
    """Mock de OdooManager para evitar conexiones reales a Odoo."""
    manager = MagicMock()
    manager.is_connected = True
    manager.is_user_authorized.return_value = True
    manager.get_filter_options.return_value = {
        'grupos': [{'id': 1, 'display_name': 'Alimentos'}, {'id': 2, 'display_name': 'Medicamentos'}],
        'lineas': [{'id': 10, 'display_name': 'Línea A'}, {'id': 11, 'display_name': 'Línea B'}],
        'lugares': [{'id': 100, 'display_name': 'ALMC/Stock/Comercial'}],
    }
    manager.get_stock_inventory.return_value = [
        {
            'product_id': 1,
            'grupo_articulo': 'Alimentos',
            'linea_comercial': 'Línea A',
            'cod_articulo': 'PROD001',
            'producto': 'Producto de Prueba',
            'um': 'UND',
            'lugar': 'P≥12',
            'lote': 'L001',
            'fecha_expira': '31-12-2026',
            'cantidad_disponible': '100.00',
            'meses_expira': 9,
        }
    ]
    manager.get_export_inventory.return_value = [
        {
            'product_id': 2,
            'grupo_articulo': 'Medicamentos',
            'linea_comercial': 'Línea B',
            'cod_articulo': 'PROD002',
            'producto': 'Producto Exportación',
            'um': 'CJA',
            'lugar': 'ALMC/Stock/PCP/Exportacion',
            'lote': 'L002',
            'fecha_expira': '15-06-2026',
            'cantidad_disponible': '50.00',
            'meses_expira': 3,
        }
    ]
    manager.get_dashboard_data.return_value = {
        'kpi_total_products': 1,
        'kpi_total_quantity': 100,
        'kpi_vence_pronto': 0,
        'chart_labels': ['Producto de Prueba'],
        'chart_data': [100.0],
        'chart_ids': [1],
        'exp_chart_labels': [],
        'exp_chart_data': [],
        'exp_by_line_labels': [],
        'exp_by_line_data': [],
        'expiring_soon_labels': [],
        'expiring_soon_data': [],
        'expiring_soon_ids': [],
        'category_stock_labels': ['Alimentos'],
        'category_stock_data': [100.0],
        'line_stock_labels': ['Línea A'],
        'line_stock_data': [100.0],
    }
    return manager


@pytest.fixture
def mock_analytics_db():
    """Mock de AnalyticsDB para evitar conexiones reales a la BD."""
    db = MagicMock()
    db.log_visit.return_value = True
    db.get_total_visits.return_value = 42
    db.get_unique_users.return_value = 5
    db.get_visits_by_user.return_value = [
        {'user_email': 'test@example.com', 'user_name': 'Test User', 'visit_count': 10, 'last_visit': None}
    ]
    db.get_visits_by_page.return_value = []
    db.get_visits_by_day.return_value = []
    db.get_visits_by_hour.return_value = []
    db.get_recent_visits.return_value = []
    return db


@pytest.fixture(scope='session')
def _app_module():
    """
    Importa el módulo app una sola vez por sesión de pytest, con dependencias mockeadas.
    Usa patching persistente que dura toda la sesión.
    """
    import sys

    # Limpiar módulos cacheados para forzar re-importación limpia
    for mod_name in list(sys.modules.keys()):
        if mod_name in ('app',):
            del sys.modules[mod_name]

    stub_om = MagicMock()
    stub_om.is_connected = False
    stub_om.get_filter_options.return_value = {'grupos': [], 'lineas': [], 'lugares': []}
    stub_db = MagicMock()

    with patch('odoo_manager.OdooManager', return_value=stub_om), \
         patch('analytics_db.AnalyticsDB', return_value=stub_db):
        import app as app_module  # importación fresca con stubs

    # Configurar para testing fuera del patch (secret_key fijo)
    app_module.app.config.update({
        'TESTING': True,
        'SECRET_KEY': 'test-secret-key-for-testing-only',
        'WTF_CSRF_ENABLED': False,
        'SESSION_COOKIE_SECURE': False,
    })
    return app_module


@pytest.fixture
def app(mock_odoo_manager, mock_analytics_db, _app_module):
    """
    Devuelve la instancia Flask configurada para testing con mocks frescos por test.
    """
    _app_module.data_manager = mock_odoo_manager
    _app_module.analytics_db = mock_analytics_db
    yield _app_module.app


@pytest.fixture
def client(app):
    """Cliente HTTP para hacer requests de prueba."""
    with app.test_client() as c:
        yield c


@pytest.fixture
def authenticated_session(client):
    """Cliente con sesión autenticada activa."""
    from datetime import datetime
    with client.session_transaction() as sess:
        sess['username'] = 'jonathan.cerda@agrovetmarket.com'
        sess['user_name'] = 'Jonathan Cerda'
        sess['last_activity'] = datetime.now().isoformat()
    return client


@pytest.fixture
def sample_inventory():
    """Datos de inventario de ejemplo para tests unitarios."""
    return [
        {
            'product_id': 1,
            'grupo_articulo': 'Alimentos',
            'linea_comercial': 'Línea A',
            'cod_articulo': 'PROD001',
            'producto': 'Producto Alpha',
            'um': 'UND',
            'lugar': 'P≥12',
            'lote': 'L001',
            'fecha_expira': '31-12-2026',
            'cantidad_disponible': '100.00',
            'meses_expira': 9,
        },
        {
            'product_id': 2,
            'grupo_articulo': 'Medicamentos',
            'linea_comercial': 'Línea B',
            'cod_articulo': 'PROD002',
            'producto': 'Producto Beta',
            'um': 'CJA',
            'lugar': '0≥P≤3',
            'lote': 'L002',
            'fecha_expira': '15-03-2026',
            'cantidad_disponible': '25.50',
            'meses_expira': 2,
        },
        {
            'product_id': 3,
            'grupo_articulo': 'Alimentos',
            'linea_comercial': 'Línea A',
            'cod_articulo': 'PROD003',
            'producto': 'Producto Gamma',
            'um': 'UND',
            'lugar': '3>P<6',
            'lote': 'L003',
            'fecha_expira': '30-06-2026',
            'cantidad_disponible': '200.00',
            'meses_expira': None,
        },
    ]
