"""
Tests para schemas.py — Validación de entradas con Pydantic
"""
import pytest
from pydantic import ValidationError
from schemas import (
    InventoryFilters,
    ExportFilters,
    ExportacionFilters,
    DashboardFilters,
    AnalyticsFilters,
)


class TestEmptyStringCoercion:
    """El model_validator base debe convertir strings vacíos a None."""

    def test_empty_string_becomes_none_in_int_field(self):
        f = InventoryFilters.model_validate({'category_id': ''})
        assert f.category_id is None

    def test_whitespace_string_becomes_none(self):
        f = InventoryFilters.model_validate({'search_term': '   '})
        assert f.search_term is None

    def test_none_stays_none(self):
        f = InventoryFilters.model_validate({'product_id': None})
        assert f.product_id is None

    def test_valid_string_int_coerces_to_int(self):
        f = InventoryFilters.model_validate({'category_id': '5'})
        assert f.category_id == 5


class TestInventoryFilters:

    def test_all_none_by_default(self):
        f = InventoryFilters.model_validate({})
        assert f.search_term is None
        assert f.product_id is None
        assert f.category_id is None
        assert f.line_id is None
        assert f.location_id is None
        assert f.exp_status is None

    def test_valid_search_term(self):
        f = InventoryFilters.model_validate({'search_term': 'vitamina'})
        assert f.search_term == 'vitamina'

    def test_search_term_max_length_rejected(self):
        with pytest.raises(ValidationError):
            InventoryFilters.model_validate({'search_term': 'x' * 101})

    def test_search_term_exactly_100_accepted(self):
        f = InventoryFilters.model_validate({'search_term': 'a' * 100})
        assert len(f.search_term) == 100

    def test_valid_exp_status_values(self):
        for val in ('0-3', '3-6', '6-9', '9-12'):
            f = InventoryFilters.model_validate({'exp_status': val})
            assert f.exp_status == val

    def test_invalid_exp_status_rejected(self):
        with pytest.raises(ValidationError):
            InventoryFilters.model_validate({'exp_status': 'invalido'})

    def test_negative_category_id_rejected(self):
        with pytest.raises(ValidationError):
            InventoryFilters.model_validate({'category_id': -1})

    def test_zero_category_id_rejected(self):
        with pytest.raises(ValidationError):
            InventoryFilters.model_validate({'category_id': 0})

    def test_non_numeric_product_id_rejected(self):
        with pytest.raises(ValidationError):
            InventoryFilters.model_validate({'product_id': 'abc'})

    def test_valid_all_fields(self):
        f = InventoryFilters.model_validate({
            'search_term': 'test',
            'product_id': '10',
            'category_id': '2',
            'line_id': '3',
            'location_id': '4',
            'exp_status': '0-3',
        })
        assert f.search_term == 'test'
        assert f.product_id == 10
        assert f.category_id == 2
        assert f.exp_status == '0-3'


class TestExportFilters:

    def test_valid_exp_status_values(self):
        for val in ('vence_pronto', 'advertencia', 'ok', 'largo_plazo'):
            f = ExportFilters.model_validate({'exp_status': val})
            assert f.exp_status == val

    def test_invalid_exp_status_rejected(self):
        with pytest.raises(ValidationError):
            ExportFilters.model_validate({'exp_status': '0-3'})  # pertenece a InventoryFilters

    def test_no_location_field_does_not_exist_in_exportacion(self):
        """ExportacionFilters no tiene location_id."""
        f = ExportacionFilters.model_validate({'location_id': '5'})
        assert not hasattr(f, 'location_id')

    def test_exportacion_valid_fields(self):
        f = ExportacionFilters.model_validate({
            'search_term': 'vitamina',
            'category_id': '1',
            'line_id': '2',
        })
        assert f.search_term == 'vitamina'
        assert f.category_id == 1
        assert f.line_id == 2


class TestDashboardFilters:

    def test_defaults_all_none(self):
        f = DashboardFilters.model_validate({})
        assert f.category_id is None
        assert f.line_id is None
        assert f.location_id is None

    def test_string_ids_coerced_to_int(self):
        f = DashboardFilters.model_validate({'category_id': '7', 'line_id': '3', 'location_id': '14'})
        assert f.category_id == 7
        assert f.line_id == 3
        assert f.location_id == 14

    def test_invalid_string_rejected(self):
        with pytest.raises(ValidationError):
            DashboardFilters.model_validate({'category_id': 'texto'})


class TestAnalyticsFilters:

    def test_default_period_is_30(self):
        f = AnalyticsFilters.model_validate({})
        assert f.period == 30

    def test_valid_period(self):
        f = AnalyticsFilters.model_validate({'period': '90'})
        assert f.period == 90

    def test_period_zero_rejected(self):
        with pytest.raises(ValidationError):
            AnalyticsFilters.model_validate({'period': 0})

    def test_period_above_365_rejected(self):
        with pytest.raises(ValidationError):
            AnalyticsFilters.model_validate({'period': 366})

    def test_period_365_accepted(self):
        f = AnalyticsFilters.model_validate({'period': 365})
        assert f.period == 365
