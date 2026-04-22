# tests/test_odoo_manager.py
"""
Tests unitarios para OdooManager.
Todas las pruebas son puras (sin conexión real a Odoo).
Se instancia OdooManager con conexión parcheada para evitar llamadas de red.
"""

import pytest
from unittest.mock import patch, MagicMock


# ---------------------------------------------------------------------------
# Helpers para instanciar OdooManager sin conexión real
# ---------------------------------------------------------------------------

def _make_manager_disconnected():
    """Devuelve una instancia de OdooManager con is_connected=False, sin red."""
    with patch('odoo_manager.xmlrpc.client.ServerProxy'):
        with patch.dict('os.environ', {
            'ODOO_URL': 'http://localhost:8069',
            'ODOO_DB': 'testdb',
            'ODOO_USER': 'test@test.com',
            'ODOO_PASSWORD': 'testpass',
        }):
            from odoo_manager import OdooManager
            manager = OdooManager.__new__(OdooManager)
            manager.url = 'http://localhost:8069'
            manager.db = 'testdb'
            manager.user = 'test@test.com'
            manager.password = 'testpass'
            manager.uid = None
            manager.models = None
            manager.is_connected = False
            manager.whitelist = set()
            return manager


# ---------------------------------------------------------------------------
# _transform_location_name — método estático puro
# ---------------------------------------------------------------------------

class TestTransformLocationName:
    """Tests para la transformación de nombres de ubicaciones."""

    def setup_method(self):
        from odoo_manager import OdooManager
        self.fn = OdooManager._transform_location_name

    @pytest.mark.parametrize("input_name, expected", [
        ('ALMC/Stock/Corto Vencimiento/VCTO1A3M', '0≥P≤3'),
        ('ALMC/Stock/Corto Vencimiento/VCTO3A6M', '3>P<6'),
        ('ALMC/Stock/Corto Vencimiento/VCTO6A9M', '6≥P<9'),
        ('ALMC/Stock/Corto Vencimiento/VCTO9A12M', '9≥P≤12'),
        ('ALMC/Stock/Comercial', 'P≥12'),
    ])
    def test_known_transformations(self, input_name, expected):
        assert self.fn(input_name) == expected

    def test_unknown_name_returns_original(self):
        assert self.fn('ALMC/Stock/Nuevo') == 'ALMC/Stock/Nuevo'

    def test_empty_string_returns_empty(self):
        assert self.fn('') == ''


# ---------------------------------------------------------------------------
# _get_related_name — método estático puro
# ---------------------------------------------------------------------------

class TestGetRelatedName:
    """Tests para extraer el nombre de una tupla de relación Odoo."""

    def setup_method(self):
        from odoo_manager import OdooManager
        self.fn = OdooManager._get_related_name

    def test_valid_list_returns_name(self):
        assert self.fn([42, 'Categoría Frutas']) == 'Categoría Frutas'

    def test_single_element_list_returns_empty(self):
        assert self.fn([42]) == ''

    def test_false_value_returns_empty(self):
        assert self.fn(False) == ''

    def test_none_returns_empty(self):
        assert self.fn(None) == ''

    def test_empty_list_returns_empty(self):
        assert self.fn([]) == ''

    def test_string_returns_empty(self):
        assert self.fn('nombre directo') == ''


# ---------------------------------------------------------------------------
# _process_expiration_date — método estático puro
# ---------------------------------------------------------------------------

class TestProcessExpirationDate:
    """Tests para el procesamiento de fechas de vencimiento."""

    def setup_method(self):
        from odoo_manager import OdooManager
        self.fn = OdooManager._process_expiration_date

    def test_none_returns_empty_tuple(self):
        date_str, months = self.fn(None)
        assert date_str == ''
        assert months is None

    def test_empty_string_returns_empty_tuple(self):
        date_str, months = self.fn('')
        assert date_str == ''
        assert months is None

    def test_valid_date_formats_correctly(self):
        date_str, months = self.fn('2030-12-31')
        assert date_str == '31-12-2030'
        assert isinstance(months, int)

    def test_valid_date_months_is_positive_for_future(self):
        _, months = self.fn('2099-01-01')
        assert months > 0

    def test_date_with_time_component_parsed(self):
        date_str, months = self.fn('2030-06-15 00:00:00')
        assert date_str == '15-06-2030'

    def test_invalid_date_returns_original(self):
        date_str, months = self.fn('no-es-una-fecha')
        assert date_str == 'no-es-una-fecha'
        assert months is None


# ---------------------------------------------------------------------------
# is_user_authorized — lógica de whitelist
# ---------------------------------------------------------------------------

class TestIsUserAuthorized:
    """Tests para la verificación de whitelist."""

    def test_empty_whitelist_allows_everyone(self):
        manager = _make_manager_disconnected()
        manager.whitelist = set()
        assert manager.is_user_authorized('cualquiera@ejemplo.com') is True

    def test_user_in_whitelist_is_authorized(self):
        manager = _make_manager_disconnected()
        manager.whitelist = {'juan@agrovetmarket.com', 'maria@agrovetmarket.com'}
        assert manager.is_user_authorized('juan@agrovetmarket.com') is True

    def test_user_not_in_whitelist_is_denied(self):
        manager = _make_manager_disconnected()
        manager.whitelist = {'juan@agrovetmarket.com'}
        assert manager.is_user_authorized('otro@externo.com') is False

    def test_comparison_is_case_insensitive(self):
        manager = _make_manager_disconnected()
        manager.whitelist = {'juan@agrovetmarket.com'}
        assert manager.is_user_authorized('JUAN@AGROVETMARKET.COM') is True

    def test_user_with_mixed_case_in_set(self):
        manager = _make_manager_disconnected()
        manager.whitelist = {'juan@agrovetmarket.com'}
        # Si por alguna razón se almacenó en mayúsculas, igual debe comparar bien
        assert manager.is_user_authorized('Juan@Agrovetmarket.com') is True


# ---------------------------------------------------------------------------
# get_stock_inventory — desconectado debe retornar lista vacía
# ---------------------------------------------------------------------------

class TestGetStockInventoryDisconnected:
    """Tests para get_stock_inventory sin conexión."""

    def test_returns_empty_list_when_disconnected(self):
        manager = _make_manager_disconnected()
        result = manager.get_stock_inventory()
        assert result == []

    def test_returns_empty_list_with_search_term(self):
        manager = _make_manager_disconnected()
        result = manager.get_stock_inventory(search_term='amoxicilina')
        assert result == []

    def test_returns_empty_list_with_category_filter(self):
        manager = _make_manager_disconnected()
        result = manager.get_stock_inventory(category_id=5)
        assert result == []

    def test_returns_list_type(self):
        manager = _make_manager_disconnected()
        result = manager.get_stock_inventory()
        assert isinstance(result, list)


# ---------------------------------------------------------------------------
# get_export_inventory — desconectado debe retornar lista vacía
# ---------------------------------------------------------------------------

class TestGetExportInventoryDisconnected:
    """Tests para get_export_inventory sin conexión."""

    def test_returns_empty_list_when_disconnected(self):
        manager = _make_manager_disconnected()
        result = manager.get_export_inventory()
        assert result == []

    def test_returns_list_type(self):
        manager = _make_manager_disconnected()
        result = manager.get_export_inventory()
        assert isinstance(result, list)


# ---------------------------------------------------------------------------
# _get_dashboard_data_internal — inventario vacío retorna zeros
# ---------------------------------------------------------------------------

class TestGetDashboardDataInternal:
    """Tests para la lógica interna del dashboard."""

    def test_empty_inventory_returns_zero_kpis(self):
        manager = _make_manager_disconnected()
        with patch.object(manager, 'get_stock_inventory', return_value=[]):
            result = manager._get_dashboard_data_internal()
        assert result['kpi_total_products'] == 0
        assert result['kpi_total_quantity'] == 0
        assert result['kpi_vence_pronto'] == 0

    def test_empty_inventory_returns_empty_charts(self):
        manager = _make_manager_disconnected()
        with patch.object(manager, 'get_stock_inventory', return_value=[]):
            result = manager._get_dashboard_data_internal()
        assert result['chart_labels'] == []
        assert result['chart_data'] == []
        assert result['category_stock_labels'] == []

    def test_empty_inventory_returns_complete_keys(self):
        """Verifica que el dict tenga todas las claves esperadas."""
        manager = _make_manager_disconnected()
        with patch.object(manager, 'get_stock_inventory', return_value=[]):
            result = manager._get_dashboard_data_internal()
        expected_keys = [
            'kpi_total_products', 'kpi_total_quantity', 'kpi_vence_pronto',
            'chart_labels', 'chart_data', 'chart_ids',
            'exp_chart_labels', 'exp_chart_data',
            'exp_by_line_labels', 'exp_by_line_data',
            'expiring_soon_labels', 'expiring_soon_data', 'expiring_soon_ids',
            'category_stock_labels', 'category_stock_data',
            'line_stock_labels', 'line_stock_data',
        ]
        for key in expected_keys:
            assert key in result, f"Clave faltante en resultado: {key}"

    def test_with_inventory_counts_products(self):
        manager = _make_manager_disconnected()
        inventory = [
            {
                'product_id': 1,
                'producto': 'Producto A',
                'grupo_articulo': 'Grupo 1',
                'linea_comercial': 'Línea 1',
                'cantidad_disponible': '100.00',
                'fecha_expira': '31-12-2030',
                'meses_expira': 48,
                'lugar': 'P≥12',
            },
            {
                'product_id': 2,
                'producto': 'Producto B',
                'grupo_articulo': 'Grupo 2',
                'linea_comercial': 'Línea 1',
                'cantidad_disponible': '50.00',
                'fecha_expira': '15-06-2026',
                'meses_expira': 3,
                'lugar': '0≥P≤3',
            },
        ]
        with patch.object(manager, 'get_stock_inventory', return_value=inventory):
            result = manager._get_dashboard_data_internal()
        assert result['kpi_total_products'] == 2

    def test_kpi_vence_pronto_sums_quantity_expiring_0_to_3_months(self):
        """
        kpi_vence_pronto suma la cantidad disponible de productos que vencen en 0-3 meses,
        NO cuenta el número de productos.
        """
        manager = _make_manager_disconnected()
        inventory = [
            {
                'product_id': 1, 'producto': 'Expira Hoy',
                'grupo_articulo': 'G1', 'linea_comercial': 'L1',
                'cantidad_disponible': '10.00', 'fecha_expira': '01-01-2026',
                'meses_expira': 0,
            },
            {
                'product_id': 2, 'producto': 'Expira Lejos',
                'grupo_articulo': 'G1', 'linea_comercial': 'L1',
                'cantidad_disponible': '20.00', 'fecha_expira': '01-01-2030',
                'meses_expira': 48,
            },
        ]
        with patch.object(manager, 'get_stock_inventory', return_value=inventory):
            result = manager._get_dashboard_data_internal()
        # Solo el primer producto vence en 0-3 meses → suma cantidad = 10
        assert result['kpi_vence_pronto'] == 10

    def test_kpi_vence_pronto_excludes_products_outside_range(self):
        """Productos con meses_expira > 3 no se incluyen en kpi_vence_pronto."""
        manager = _make_manager_disconnected()
        inventory = [
            {
                'product_id': 1, 'producto': 'No Vence Pronto',
                'grupo_articulo': 'G1', 'linea_comercial': 'L1',
                'cantidad_disponible': '100.00', 'fecha_expira': '01-01-2030',
                'meses_expira': 48,
            },
        ]
        with patch.object(manager, 'get_stock_inventory', return_value=inventory):
            result = manager._get_dashboard_data_internal()
        assert result['kpi_vence_pronto'] == 0
