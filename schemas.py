"""
Schemas de validación de entradas — Inventario Stock Web
=========================================================
Basado en OWASP A03:2021 - Injection / A01:2021 - Broken Access Control
Referencia: docs/SECURE_CODING_GUIDELINES.md sección 3

Todos los schemas heredan de _FilterBase, que convierte strings vacíos
a None antes de la validación (compatibilidad con request.form / request.args).
"""
from pydantic import BaseModel, Field, model_validator
from typing import Optional, Literal, Any


class _FilterBase(BaseModel):
    """Base con coerción de string vacío → None para compatibilidad con Flask request."""

    @model_validator(mode='before')
    @classmethod
    def _empty_str_to_none(cls, data: Any) -> Any:
        if isinstance(data, dict):
            return {
                k: None if (isinstance(v, str) and not v.strip()) else v
                for k, v in data.items()
            }
        return data


# ---------------------------------------------------------------------------
# Tipos literales para exp_status — previene valores arbitrarios
# ---------------------------------------------------------------------------
_ExpStatusInventory = Optional[Literal['0-3', '3-6', '6-9', '9-12']]
_ExpStatusExport = Optional[Literal['vence_pronto', 'advertencia', 'ok', 'largo_plazo']]


# ---------------------------------------------------------------------------
# Schemas públicos
# ---------------------------------------------------------------------------

class InventoryFilters(_FilterBase):
    """Filtros para GET|POST /inventory."""

    search_term: Optional[str] = Field(None, max_length=100)
    product_id: Optional[int] = Field(None, ge=1)
    category_id: Optional[int] = Field(None, ge=1)
    line_id: Optional[int] = Field(None, ge=1)
    location_id: Optional[int] = Field(None, ge=1)
    exp_status: _ExpStatusInventory = None


class ExportFilters(_FilterBase):
    """Filtros para GET /export/excel."""

    search_term: Optional[str] = Field(None, max_length=100)
    product_id: Optional[int] = Field(None, ge=1)
    category_id: Optional[int] = Field(None, ge=1)
    line_id: Optional[int] = Field(None, ge=1)
    location_id: Optional[int] = Field(None, ge=1)
    exp_status: _ExpStatusExport = None


class ExportacionFilters(_FilterBase):
    """Filtros para GET /export/excel/exportacion."""

    search_term: Optional[str] = Field(None, max_length=100)
    category_id: Optional[int] = Field(None, ge=1)
    line_id: Optional[int] = Field(None, ge=1)


class DashboardFilters(_FilterBase):
    """Filtros para GET|POST /dashboard."""

    category_id: Optional[int] = Field(None, ge=1)
    line_id: Optional[int] = Field(None, ge=1)
    location_id: Optional[int] = Field(None, ge=1)


class AnalyticsFilters(_FilterBase):
    """Filtros para GET /analytics."""

    period: int = Field(30, ge=1, le=365)
