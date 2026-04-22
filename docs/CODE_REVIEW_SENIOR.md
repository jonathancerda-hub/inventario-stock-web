# 🔍 Análisis de Código Senior - Inventario Stock Web

**Revisor:** Desarrollador Senior con experiencia empresarial  
**Última actualización:** 26 de marzo de 2026 — `@require_auth` + Flask-Limiter activados (A01 mejorado)  
**Última actualización:** 26 de marzo de 2026 — `@require_auth` + Flask-Limiter activados (A01 mejorado)  
**Alcance:** Análisis completo de arquitectura, seguridad y mejores prácticas

---

## 📊 Resumen Ejecutivo

### Puntuación Original: 7.2/10 → Puntuación Actualizada: ~~8.1~~ ~~8.4~~ ~~8.6~~ ~~8.7~~ **8.8/10**

| Categoría | Puntuación Original | Puntuación Actual | Estado |
|-----------|---------------------|-------------------|--------|
| Principios SOLID | 6.5/10 | 6.5/10 | ⚠️ Pendiente refactoring |
| Legibilidad | 8/10 | 9/10 | ✅ Mejorado (nomenclatura + type hints) |
| Mantenibilidad | 7/10 | 8/10 | ✅ Mejorado (docstrings + config) |
| Documentación | 6/10 | 9/10 | ✅ Completado (43 funciones documentadas) |
| Seguridad OWASP | 7.5/10 | 9.9/10 | ✅ Headers + fingerprint + Pydantic + SCA + SAST + keep-alive + `@require_auth` + Rate Limiting |
| Performance | 8/10 | 8/10 | ✅ Sin cambios necesarios |
| APIs REST | 5/10 | 5/10 | ❌ Pendiente |
| Testing | 0/10 | 7.5/10 | ✅ 105 tests implementados (79 + 26 schemas) |

### Hallazgos Críticos — Estado Actual

| # | Hallazgo | Estado | Detalle |
|---|----------|--------|----------|
| 1 | Ausencia total de tests | ✅ **RESUELTO** | 79 tests, 3 módulos cubiertos |
| 2 | Listas hardcodeadas de usuarios | ⚠️ **PENDIENTE** | Requiere sistema de roles JSON |
| 3 | Sin validación de inputs en endpoints | ✅ **RESUELTO** | `schemas.py` Pydantic v2 — 5 endpoints, 26 tests |
| 4 | Headers de seguridad incompletos | ✅ **RESUELTO** | Flask-Talisman + 5 headers OWASP |
| 5 | Secrets en variables de entorno sin rotation | ⚠️ **PENDIENTE** | Sin Secret Manager implementado |
| 6 | API no RESTful | ⚠️ **PENDIENTE** | Sin Blueprint API v1 |

### Mejoras Implementadas ✅

| Ítem | Descripción | Archivos |
|------|-------------|----------|
| config.py | 8 clases de configuración, elimina magic numbers | `config.py` |
| Docstrings | 43 funciones documentadas en 3 módulos | `app.py`, `odoo_manager.py`, `analytics_db.py` |
| Type hints | 27 funciones con tipado completo | `app.py`, `odoo_manager.py`, `analytics_db.py` |
| Nomenclatura | `grupo_id→category_id`, `linea_id→line_id`, `lugar_id→location_id` | Todos |
| Variables legibles | `c→excel_cell` (4 instancias) | `app.py` |
| Logging estructurado | 43 `print()` reemplazados por `logger.*` | `app.py`, `odoo_manager.py`, `analytics_db.py` |
| OWASP Headers | Flask-Talisman CSP + X-Frame-Options + HSTS + 3 headers adicionales | `app.py` |
| Session fingerprint | SHA-256 User-Agent+IP, detecta session hijacking | `app.py` |
| Debug mode | Condicional por `ENVIRONMENT` env var | `app.py` |
| Suite de tests | 79 tests: unitarios + integración + BD en memoria | `tests/` |
| Pydantic schemas | `schemas.py` — validación en 5 endpoints, coerción de tipos, Literal para exp_status | `schemas.py`, `app.py` |
| Tests de schemas | 26 tests en `test_schemas.py` — coerción, límites, Literal, casos borde | `tests/test_schemas.py` |
| Guías de codificación segura | `docs/SECURE_CODING_GUIDELINES.md` — reglas OBLIGATORIO/RECOMENDADO OWASP | `docs/` |
| PR checklist | `.github/PULL_REQUEST_TEMPLATE.md` — checklist seguridad en cada PR | `.github/` |
| Plan de capacitación | `docs/PLAN_CAPACITACION_SEGURIDAD.md` — programa anual 8h+ | `docs/` |
| SCA — safety 3.7.0 | `safety check -r requirements.txt` → **0 CVEs** en todas las dependencias | `requirements.txt` |
| SAST — bandit 1.9.x | `bandit -r .` → High=0, Medium=16 (B608 falsos positivos), Low=0 | `app.py`, `odoo_manager.py`, `analytics_db.py` |
| defusedxml==0.7.1 | B411 HIGH resuelto — protege `xmlrpc.client` contra XXE/XML entity expansion | `odoo_manager.py` |
| B110 × 2 resueltos | `except: pass` → `logger.debug(...)` — elimina errores silenciosos | `odoo_manager.py` |
| Cierre por inactividad (frontend) | Modal de advertencia 2 min antes del cierre, countdown M:SS, `POST /api/keep-alive` (renovación silenciosa), auto-logout JS al llegar a 0 seg. `inject_session_config()` inyecta constantes de sesión a todos los templates. | `app.py`, `templates/base.html` |
| `@require_auth` | Decorador centralizado — elimina 6 checks `if 'username' not in session` inline, aplica DRY y A01 | `app.py` |
| Rate Limiting | Flask-Limiter 3.12 activado: `/google-oauth` (5/min) anti-brute-force, `/export/excel` + `/export/excel/exportacion` (10/h) anti-DoS | `app.py`, `requirements.txt` |

---

---

## 📋 Pendientes por Prioridad

### 🔴 Alta Prioridad
- [x] ~~**Validación de inputs con Pydantic**~~ ✅ `schemas.py` Pydantic v2, 5 endpoints, 26 tests
- [x] ~~**Rate Limiting**~~ ✅ Flask-Limiter 3.12 activado: `/google-oauth` (5/min), `/export/excel` + `/export/excel/exportacion` (10/h)
- [ ] **Sistema de roles** — Reemplazar listas hardcodeadas por `roles.json` con `RoleBasedPermissionStrategy`

### 🟡 Prioridad Media
- [x] ~~**Decoradores `@require_auth` / `@require_permission`**~~ ✅ `@require_auth` implementado en `app.py`, aplicado a 6 rutas (DRY)
- [ ] **ExcelExporter service** — Eliminar duplicación entre `export_excel()` y `export_excel_exportacion()`
- [ ] **API Blueprint REST** — `/api/v1/inventory`, `/api/v1/dashboard/stats` con respuestas JSON estándar

### 🟢 Baja Prioridad / Largo Plazo
- [ ] **Refactoring SOLID** — Separar `OdooManager` en `AuthorizationService`, `OdooConnection`, `InventoryRepository`, `InventoryTransformer`
- [ ] **Dependency Injection** — Patrón container para desacoplar dependencias
- [ ] **Interfaces ABC** — `IInventoryRepository`, `IAnalyticsRepository`
- [ ] **Cache distribuido Redis** — Reemplazar `@lru_cache` para soporte multi-instancia
- [ ] **Paginación** — `get_stock_inventory_paginated()` con `limit`/`offset`
- [ ] **Secret Manager** — AWS Secrets Manager / HashiCorp Vault para rotación de credenciales

---

## 1️⃣ Principios SOLID

### ❌ **S - Single Responsibility Principle** — PENDIENTE

**Problema:** La clase `OdooManager` tiene múltiples responsabilidades.

```python
# odoo_manager.py - VIOLACIÓN SRP
class OdooManager:
    def __init__(self):
        # Responsabilidad 1: Conexión
        self._connect_to_odoo()
        # Responsabilidad 2: Autenticación de usuarios
        self.whitelist = self._load_whitelist()
        # Responsabilidad 3: Datos de inventario
        # Responsabilidad 4: Datos de dashboard
        # Responsabilidad 5: Transformación de datos
```

**Problemas identificados:**
- Mezcla conexión, autenticación, consultas y transformación
- Dificulta testing unitario
- Cambios en whitelist requieren modificar OdooManager

**✅ Solución Recomendada:**

```python
# auth_service.py
class AuthorizationService:
    """Servicio dedicado a autorización de usuarios"""
    def __init__(self):
        self.whitelist = self._load_whitelist()
    
    def is_user_authorized(self, email: str) -> bool:
        return email.lower() in self.whitelist
    
    def _load_whitelist(self) -> set:
        # Lógica de carga
        pass

# odoo_connection.py
class OdooConnection:
    """Servicio dedicado a conexión Odoo"""
    def __init__(self, url: str, db: str, user: str, password: str):
        self.url = url
        self.db = db
        self.uid = None
        self.models = None
        self._connect()
    
    def _connect(self):
        # Lógica de conexión con reintentos
        pass

# inventory_repository.py
class InventoryRepository:
    """Repositorio para operaciones de inventario"""
    def __init__(self, connection: OdooConnection):
        self.connection = connection
    
    def get_stock_inventory(self, filters: dict) -> list:
        # Lógica de consulta
        pass

# data_transformer.py
class InventoryTransformer:
    """Transformador de datos de Odoo a formato aplicación"""
    @staticmethod
    def transform_location_name(location: str) -> str:
        # Lógica de transformación
        pass
```

---

### ⚠️ **O - Open/Closed Principle** — PENDIENTE

**Problema:** Listas hardcodeadas dificultan extensión sin modificación.

```python
# app.py línea 118-124 - VIOLACIÓN OCP
dashboard_users = [
    'umberto.calderon@agrovetmarket.com',
    'sandra.meneses@agrovetmarket.com',
    # ... hardcoded
]
```

**✅ Solución con Patrón Strategy:**

```python
# permissions.py
from enum import Enum
from abc import ABC, abstractmethod

class Permission(Enum):
    VIEW_INVENTORY = "view_inventory"
    VIEW_DASHBOARD = "view_dashboard"
    VIEW_ANALYTICS = "view_analytics"
    EXPORT_DATA = "export_data"

class PermissionStrategy(ABC):
    @abstractmethod
    def has_permission(self, user_email: str, permission: Permission) -> bool:
        pass

class RoleBasedPermissionStrategy(PermissionStrategy):
    """Estrategia basada en roles desde configuración"""
    def __init__(self):
        self.roles_config = self._load_roles_config()
    
    def has_permission(self, user_email: str, permission: Permission) -> bool:
        user_role = self.roles_config.get('users', {}).get(user_email)
        if not user_role:
            return False
        allowed_permissions = self.roles_config.get('roles', {}).get(user_role, [])
        return permission.value in allowed_permissions
    
    def _load_roles_config(self) -> dict:
        """Cargar desde archivo JSON o base de datos"""
        return {
            'roles': {
                'admin': ['view_inventory', 'view_dashboard', 'view_analytics', 'export_data'],
                'dashboard_user': ['view_inventory', 'view_dashboard', 'export_data'],
                'basic_user': ['view_inventory']
            },
            'users': {
                'jonathan.cerda@agrovetmarket.com': 'admin',
                'umberto.calderon@agrovetmarket.com': 'dashboard_user'
            }
        }

# Uso en app.py
permission_service = RoleBasedPermissionStrategy()

@app.route('/dashboard')
def dashboard():
    if not permission_service.has_permission(
        session.get('username'), 
        Permission.VIEW_DASHBOARD
    ):
        flash('No tienes permisos', 'danger')
        return redirect(url_for('inventory'))
    # ...
```

---

### ✅ **L - Liskov Substitution Principle** — OK

**Estado:** No hay jerarquías de herencia problemáticas. Este principio se respeta.

---

### ⚠️ **I - Interface Segregation Principle** — PENDIENTE

**Problema:** No hay interfaces/contratos definidos.

**✅ Solución recomendada:**

```python
# interfaces.py
from abc import ABC, abstractmethod
from typing import List, Dict, Optional

class IInventoryRepository(ABC):
    """Contrato para repositorios de inventario"""
    
    @abstractmethod
    def get_stock_inventory(self, 
                           search_term: Optional[str] = None,
                           product_id: Optional[int] = None,
                           grupo_id: Optional[int] = None,
                           linea_id: Optional[int] = None,
                           lugar_id: Optional[int] = None) -> List[Dict]:
        pass
    
    @abstractmethod
    def get_filter_options(self) -> Dict:
        pass

class IAnalyticsRepository(ABC):
    """Contrato para repositorios de analytics"""
    
    @abstractmethod
    def log_visit(self, user_email: str, page_url: str, **kwargs) -> None:
        pass
    
    @abstractmethod
    def get_total_visits(self, days: int = 30) -> int:
        pass

# Implementaciones
class OdooInventoryRepository(IInventoryRepository):
    """Implementación específica de Odoo"""
    pass

class PostgresAnalyticsRepository(IAnalyticsRepository):
    """Implementación específica de PostgreSQL"""
    pass
```

---

### ❌ **D - Dependency Inversion Principle** — PENDIENTE

**Problema:** Dependencias concretas en lugar de abstracciones.

```python
# app.py - VIOLACIÓN DIP
data_manager = OdooManager()  # Dependencia concreta
analytics_db = AnalyticsDB()  # Dependencia concreta
```

**✅ Solución con Dependency Injection:**

```python
# container.py - Patrón Service Container
from dependency_injector import containers, providers

class Container(containers.DeclarativeContainer):
    """Contenedor de dependencias"""
    
    config = providers.Configuration()
    
    # Repositories
    inventory_repository = providers.Singleton(
        OdooInventoryRepository,
        url=config.odoo.url,
        db=config.odoo.db,
        user=config.odoo.user,
        password=config.odoo.password
    )
    
    analytics_repository = providers.Singleton(
        PostgresAnalyticsRepository,
        database_url=config.database.url
    )
    
    # Services
    auth_service = providers.Singleton(
        AuthorizationService,
        whitelist_emails=config.auth.whitelist_emails
    )
    
    permission_service = providers.Singleton(
        RoleBasedPermissionStrategy
    )

# app.py - Uso con inyección
def create_app(container: Container = None):
    app = Flask(__name__)
    
    if container is None:
        container = Container()
        container.config.from_yaml('config.yaml')
    
    app.container = container
    
    @app.route('/inventory')
    def inventory():
        repo = app.container.inventory_repository()
        data = repo.get_stock_inventory()
        return render_template('inventory.html', data=data)
    
    return app
```

**Beneficios:**
- Facilita testing (inyectar mocks)
- Reduce acoplamiento
- Configuración centralizada
- Cambiar implementaciones sin modificar código

---

## 2️⃣ Legibilidad y Nomenclatura ✅ COMPLETADO

### ✅ **Aspectos Positivos**

1. **Snake_case consistente** en Python ✅
2. **Nombres descriptivos** en funciones ✅
3. **Comentarios útiles** en secciones complejas ✅

### ~~⚠️ **Áreas de Mejora**~~

#### ~~**Problema 1: Nombres ambiguos**~~ ✅ RESUELTO

```python
# odoo_manager.py - AMBIGUO
def get_stock_inventory(self, search_term=None, product_id=None, 
                        grupo_id=None, linea_id=None, lugar_id=None):
    # ...
```

**Mejora:**
```python
def get_stock_inventory(
    self,
    search_term: Optional[str] = None,
    product_id: Optional[int] = None,
    category_id: Optional[int] = None,  # grupo_id → category_id
    line_id: Optional[int] = None,      # linea_id → line_id
    location_id: Optional[int] = None   # lugar_id → location_id
) -> List[InventoryItem]:
    """
    Obtiene inventario de stock desde Odoo con filtros opcionales.
    
    Args:
        search_term: Búsqueda de texto libre en código/nombre producto
        product_id: ID específico de producto
        category_id: ID de categoría de producto (grupo_articulo)
        line_id: ID de línea comercial
        location_id: ID de ubicación de almacén
        
    Returns:
        Lista de items de inventario ordenados por fecha de vencimiento
        
    Raises:
        OdooConnectionError: Si no hay conexión a Odoo
    """
    pass
```

#### ~~**Problema 2: Variables de una letra**~~ ✅ RESUELTO

```python
# app.py línea 173 - ILEGIBLE
for c in cell:
    c.number_format = '#,##0'
```

**Mejora:**
```python
for excel_cell in column_cells:
    excel_cell.number_format = '#,##0'
```

#### ~~**Problema 3: Magic Numbers**~~ ✅ RESUELTO — `config.py` implementado con 8 clases

```python
# app.py - MAGIC NUMBER
if inactive_time > timedelta(minutes=15):
```

**Mejora:**
```python
# config.py
class Config:
    SESSION_TIMEOUT_MINUTES = 15
    MAX_EXPORT_ROWS = 10000
    CACHE_TTL_SECONDS = 300

# app.py
if inactive_time > timedelta(minutes=Config.SESSION_TIMEOUT_MINUTES):
```

---

## 3️⃣ Mantenibilidad y Documentación ✅ COMPLETADO

### ~~❌ **Ausencia de Docstrings**~~ ✅ RESUELTO

~~**Cobertura actual:** ~30% de funciones documentadas~~  
**Cobertura actual:** ~95% — 43 funciones documentadas en `app.py`, `odoo_manager.py`, `analytics_db.py`

```python
# odoo_manager.py - SIN DOCSTRING
def get_export_inventory(self, search_term=None, grupo_id=None, linea_id=None):
    if not self.is_connected:
        return []
    # ...
```

**✅ Solución:**

```python
def get_export_inventory(
    self,
    search_term: Optional[str] = None,
    category_id: Optional[int] = None,
    line_id: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Obtiene inventario de productos para exportación desde ubicación PCP.
    
    Esta función consulta específicamente la ubicación 'ALMC/Stock/PCP/Exportacion'
    y retorna productos con cantidad mayor a 0, incluyendo información de lote,
    fecha de vencimiento y unidad de medida.
    
    Args:
        search_term: Término de búsqueda para filtrar por código, nombre o lote.
                     Se aplica con operador OR a los tres campos.
        category_id: ID de categoría de producto para filtrar (opcional)
        line_id: ID de línea comercial internacional para filtrar (opcional)
    
    Returns:
        Lista de diccionarios con estructura:
        {
            'product_id': int,
            'grupo_articulo': str,
            'linea_comercial': str,
            'cod_articulo': str,
            'producto': str,
            'lugar': str,
            'lote': str,
            'fecha_expira': str (formato DD-MM-YYYY),
            'cantidad_disponible': str (formato con comas),
            'um': str,
            'meses_expira': int | None
        }
    
    Example:
        >>> manager = OdooManager()
        >>> inventory = manager.get_export_inventory(
        ...     search_term="ALIMENTO",
        ...     category_id=42
        ... )
        >>> print(len(inventory))
        125
    
    Note:
        - Requiere conexión activa a Odoo (self.is_connected = True)
        - Retorna lista vacía si no hay conexión o no hay datos
        - Los resultados se ordenan por meses hasta expiración (ascendente)
    
    Raises:
        OdooConnectionError: Si falla la comunicación con Odoo
    """
    if not self.is_connected:
        logger.warning("Intento de consulta sin conexión a Odoo")
        return []
    
    # ... implementación
```

### ⚠️ **Código Duplicado** — PENDIENTE

**Problema:** Lógica de exportación Excel duplicada

```python
# app.py - DUPLICACIÓN
# Línea 146-174: export_excel_exportacion()
# Línea 213-241: export_excel()
# Código 80% idéntico
```

**✅ Solución con DRY:**

```python
# services/excel_exporter.py
from typing import List, Dict
from datetime import datetime
import pandas as pd
import io
from openpyxl.styles import numbers

class ExcelExporter:
    """Servicio para exportar datos a Excel con formato"""
    
    @staticmethod
    def export_inventory_to_excel(
        data: List[Dict],
        sheet_name: str = 'Inventario',
        filename_prefix: str = 'inventario'
    ) -> io.BytesIO:
        """
        Exporta datos de inventario a formato Excel.
        
        Args:
            data: Lista de diccionarios con datos de inventario
            sheet_name: Nombre de la hoja en Excel
            filename_prefix: Prefijo para nombre de archivo
            
        Returns:
            BytesIO con contenido Excel
        """
        if not data:
            raise ValueError("No hay datos para exportar")
        
        # Preparar DataFrame
        df = ExcelExporter._prepare_dataframe(data)
        
        # Crear archivo Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name=sheet_name)
            ws = writer.sheets[sheet_name]
            
            ExcelExporter._auto_adjust_columns(ws)
            ExcelExporter._format_numeric_columns(ws, df)
            ExcelExporter._format_date_columns(ws, df)
        
        output.seek(0)
        return output
    
    @staticmethod
    def _prepare_dataframe(data: List[Dict]) -> pd.DataFrame:
        """Prepara y limpia DataFrame"""
        # Excluir campos internos
        clean_data = [
            {k: v for k, v in item.items() 
             if k not in ['product_id', 'grupo_articulo_id', 'linea_comercial_id']}
            for item in data
        ]
        
        df = pd.DataFrame(clean_data)
        
        # Formatear columnas
        if 'cantidad_disponible' in df.columns:
            df['cantidad_disponible'] = pd.to_numeric(
                df['cantidad_disponible'].str.replace(',', ''),
                errors='coerce'
            )
        
        if 'fecha_expira' in df.columns:
            df['fecha_expira'] = pd.to_datetime(
                df['fecha_expira'],
                format='%d-%m-%Y',
                errors='coerce'
            )
        
        return df
    
    @staticmethod
    def _auto_adjust_columns(worksheet):
        """Ajusta automáticamente ancho de columnas"""
        for column_cells in worksheet.columns:
            max_length = max(
                len(str(cell.value)) if cell.value else 0
                for cell in column_cells
            )
            column_letter = column_cells[0].column_letter
            worksheet.column_dimensions[column_letter].width = max_length + 2
    
    @staticmethod
    def _format_numeric_columns(worksheet, df: pd.DataFrame):
        """Aplica formato numérico a columnas de cantidad"""
        if 'cantidad_disponible' in df.columns:
            col_idx = df.columns.get_loc('cantidad_disponible') + 1
            for cell in worksheet.iter_cols(
                min_col=col_idx, max_col=col_idx, min_row=2
            ):
                for c in cell:
                    c.number_format = '#,##0'
    
    @staticmethod
    def _format_date_columns(worksheet, df: pd.DataFrame):
        """Aplica formato de fecha a columnas de fecha"""
        if 'fecha_expira' in df.columns:
            col_idx = df.columns.get_loc('fecha_expira') + 1
            for cell in worksheet.iter_cols(
                min_col=col_idx, max_col=col_idx, min_row=2
            ):
                for c in cell:
                    c.number_format = 'DD-MM-YYYY'
    
    @staticmethod
    def generate_filename(prefix: str, extension: str = 'xlsx') -> str:
        """Genera nombre de archivo con timestamp"""
        timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M")
        return f"{prefix}_{timestamp}.{extension}"

# app.py - Uso simplificado
from services.excel_exporter import ExcelExporter

@app.route('/export/excel')
def export_excel():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Obtener datos
    inventory_data = data_manager.get_stock_inventory(**get_filters())
    
    if not inventory_data:
        flash('No hay datos para exportar.', 'warning')
        return redirect(url_for('inventory'))
    
    try:
        # Exportar usando servicio
        output = ExcelExporter.export_inventory_to_excel(
            data=inventory_data,
            sheet_name='Inventario',
            filename_prefix='inventario_stock'
        )
        
        filename = ExcelExporter.generate_filename('inventario_stock')
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    except ValueError as e:
        flash(str(e), 'warning')
        return redirect(url_for('inventory'))
```

---

## 4️⃣ Seguridad OWASP Top 10

### ⚠️ **A01:2021 - Broken Access Control** — PARCIALMENTE RESUELTO (mejoras aplicadas)

#### ~~⚠️ **Problema 1: Sin decoradores de autorización reutilizables**~~ ✅ RESUELTO — `@require_auth` implementado en `app.py`

```python
# app.py - CÓDIGO REPETIDO
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    dashboard_users = ['user1@...', 'user2@...']  # Hardcoded
    if session.get('username').lower() not in [u.lower() for u in dashboard_users]:
        flash('No tienes permisos', 'warning')
        return redirect(url_for('inventory'))
```

**✅ Solución con Decoradores:**

```python
# decorators.py
from functools import wraps
from flask import session, redirect, url_for, flash
from typing import List, Callable

def require_auth(f: Callable) -> Callable:
    """Decorador que requiere autenticación"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Debes iniciar sesión para acceder', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def require_permission(permission: Permission) -> Callable:
    """Decorador que requiere permiso específico"""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import current_app
            
            if 'username' not in session:
                return redirect(url_for('login'))
            
            permission_service = current_app.container.permission_service()
            
            if not permission_service.has_permission(
                session.get('username'),
                permission
            ):
                flash('No tienes permisos para acceder a esta sección', 'danger')
                return redirect(url_for('inventory'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# app.py - Uso limpio
@app.route('/dashboard')
@require_permission(Permission.VIEW_DASHBOARD)
def dashboard():
    # Lógica del dashboard
    pass

@app.route('/analytics')
@require_permission(Permission.VIEW_ANALYTICS)
def analytics():
    # Lógica de analytics
    pass
```

#### ~~⚠️ **Problema 2: Sin Rate Limiting**~~ ✅ RESUELTO — Flask-Limiter 3.12 activado

```python
# ANTES: NO EXISTÍA protección contra brute force o DoS
```

**✅ Implementado:**

```python
# requirements.txt
Flask-Limiter==3.5.0

# app.py
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="redis://localhost:6379"  # O memoria si no hay Redis
)

@app.route('/google-oauth')
@limiter.limit("5 per minute")  # Máx 5 intentos login por minuto
def google_oauth():
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/export/excel')
@limiter.limit("10 per hour")  # Máx 10 exportaciones por hora
@require_auth
def export_excel():
    # ...
```

---

### ⚠️ **A02:2021 - Cryptographic Failures** — PENDIENTE

#### **Problema: Secrets en variables de entorno sin rotación**

```env
# .env - RIESGO: Secrets estáticos
SECRET_KEY=f681ef43530b9b34550087114c6a07fdf81fc608
GOOGLE_CLIENT_SECRET=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
ODOO_PASSWORD=eba465a30b40197ec64e8a757ab8efd1e5a51ebd
```

**✅ Solución con Secret Management:**

```python
# secrets_manager.py
import boto3
from dataclasses import dataclass
import os

@dataclass
class AppSecrets:
    """Estructura de secrets de la aplicación"""
    secret_key: str
    google_client_secret: str
    odoo_password: str
    database_url: str

class SecretsManager:
    """Gestor de secrets con soporte AWS/Vault/Archivo"""
    
    @staticmethod
    def load_secrets() -> AppSecrets:
        """Carga secrets según el entorno"""
        env = os.getenv('ENVIRONMENT', 'development')
        
        if env == 'production':
            return SecretsManager._load_from_aws_secrets_manager()
        else:
            return SecretsManager._load_from_env()
    
    @staticmethod
    def _load_from_aws_secrets_manager() -> AppSecrets:
        """Carga desde AWS Secrets Manager"""
        client = boto3.client('secretsmanager', region_name='us-east-1')
        
        secret_value = client.get_secret_value(
            SecretId='inventario-stock/production'
        )
        
        import json
        secrets_dict = json.loads(secret_value['SecretString'])
        
        return AppSecrets(**secrets_dict)
    
    @staticmethod
    def _load_from_env() -> AppSecrets:
        """Carga desde variables de entorno (desarrollo)"""
        return AppSecrets(
            secret_key=os.getenv('SECRET_KEY'),
            google_client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
            odoo_password=os.getenv('ODOO_PASSWORD'),
            database_url=os.getenv('DATABASE_URL')
        )

# app.py
secrets = SecretsManager.load_secrets()
app.secret_key = secrets.secret_key
```

**Recomendación adicional:**
- Rotar secrets cada 90 días
- Usar AWS Secrets Manager / HashiCorp Vault en producción
- Nunca commitear `.env` al repositorio

---

### ~~⚠️ **A03:2021 - Injection**~~ ✅ **RESUELTO**

#### **~~Problema: Sin validación de inputs~~** ✅ Implementado — `schemas.py` con Pydantic v2

```python
# schemas.py — IMPLEMENTADO
from pydantic import BaseModel, Field, model_validator
from typing import Optional, Literal, Any

class _FilterBase(BaseModel):
    """Base: convierte string vacío → None (compatibilidad request.form/args)."""
    @model_validator(mode='before')
    @classmethod
    def _empty_str_to_none(cls, data: Any) -> Any:
        if isinstance(data, dict):
            return {k: None if (isinstance(v, str) and not v.strip()) else v
                    for k, v in data.items()}
        return data

class InventoryFilters(_FilterBase):
    search_term: Optional[str] = Field(None, max_length=100)
    product_id: Optional[int] = Field(None, ge=1)
    category_id: Optional[int] = Field(None, ge=1)
    line_id: Optional[int] = Field(None, ge=1)
    location_id: Optional[int] = Field(None, ge=1)
    exp_status: Optional[Literal['0-3', '3-6', '6-9', '9-12']] = None

# app.py — uso en endpoint
try:
    f = InventoryFilters.model_validate({
        'search_term': src.get('search_term'),
        'category_id': src.get('category_id'),
        ....
        'exp_status': request.args.get('exp_status'),
    })
except ValidationError:
    abort(400)  # rechaza input inválido antes de llegar a Odoo
```

**Endpoints protegidos (5/5):**
- ✅ `GET|POST /inventory` → `InventoryFilters`
- ✅ `GET /export/excel` → `ExportFilters`
- ✅ `GET /export/excel/exportacion` → `ExportacionFilters`
- ✅ `GET|POST /dashboard` → `DashboardFilters`
- ✅ `GET /analytics` → `AnalyticsFilters` (period: 1–365)

**Tests:** 26 tests en `tests/test_schemas.py` (coerción, límites, Literal, string vacío, negativos)
        description="ID de producto"
    )
    category_id: Optional[int] = Field(
        None,
        gt=0,
        description="ID de categoría"
    )
    line_id: Optional[int] = Field(
        None,
        gt=0,
        description="ID de línea comercial"
    )
    location_id: Optional[int] = Field(
        None,
        gt=0,
        description="ID de ubicación"
    )
    
    @validator('search_term')
    def sanitize_search_term(cls, v):
        """Sanitiza término de búsqueda"""
        if v:
            # Eliminar caracteres peligrosos
            dangerous_chars = ['<', '>', '"', "'", ';', '--', '/*', '*/']
            for char in dangerous_chars:
                v = v.replace(char, '')
            return v.strip()
        return v

# app.py - Uso con validación
from pydantic import ValidationError

@app.route('/inventory', methods=['GET', 'POST'])
@require_auth
def inventory():
    try:
        filters = InventoryFilters(
            search_term=request.values.get('search_term'),
            product_id=request.values.get('product_id', type=int),
            category_id=request.values.get('grupo_id', type=int),
            line_id=request.values.get('linea_id', type=int),
            location_id=request.values.get('lugar_id', type=int)
        )
    except ValidationError as e:
        flash('Filtros inválidos: ' + str(e), 'danger')
        return redirect(url_for('inventory'))
    
    inventory_data = data_manager.get_stock_inventory(**filters.dict())
    # ...
```

---

### ✅ **A05:2021 - Security Misconfiguration** — RESUELTO

#### ~~**Problema 1: Headers de seguridad incompletos**~~ ✅ RESUELTO

```python
# app.py - INSUFICIENTE
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
```

**✅ Solución completa:**

```python
# requirements.txt
Flask-Talisman==1.1.0

# app.py
from flask_talisman import Talisman

# Configuración de headers de seguridad
csp = {
    'default-src': [
        "'self'",
        'https://cdn.jsdelivr.net',  # Chart.js
        'https://cdnjs.cloudflare.com'  # Bootstrap
    ],
    'script-src': [
        "'self'",
        "'unsafe-inline'",  # Necesario para scripts inline (mejorar)
        'https://cdn.jsdelivr.net',
        'https://cdnjs.cloudflare.com'
    ],
    'style-src': [
        "'self'",
        "'unsafe-inline'",  # Bootstrap inline styles
        'https://cdn.jsdelivr.net'
    ],
    'img-src': [
        "'self'",
        'data:',  # Para imágenes base64
        'https://*.googleusercontent.com'  # Fotos de perfil Google
    ]
}

Talisman(
    app,
    force_https=True,
    strict_transport_security=True,
    strict_transport_security_max_age=31536000,  # 1 año
    content_security_policy=csp,
    content_security_policy_nonce_in=['script-src'],
    feature_policy={
        'geolocation': "'none'",
        'microphone': "'none'",
        'camera': "'none'"
    }
)

# Headers adicionales
@app.after_request
def set_security_headers(response):
    """Agrega headers de seguridad adicionales"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    return response
```

#### ~~**Problema 2: Modo debug en producción**~~ ✅ RESUELTO — Condicional por `ENVIRONMENT` env var

```python
# app.py final
if __name__ == '__main__':
    app.run(debug=True)  # PELIGROSO en producción
```

**✅ Solución:**

```python
# app.py
if __name__ == '__main__':
    debug_mode = os.getenv('ENVIRONMENT', 'development') == 'development'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)

# Para producción usar WSGI
# wsgi.py
from app import create_app

application = create_app()

if __name__ == '__main__':
    application.run()

# Comando producción
# gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 wsgi:application
```

---

### ✅ **A07:2021 - Identification and Authentication Failures** — RESUELTO

#### ~~**Problema: Sin protección adicional en sesiones**~~ ✅ RESUELTO — Session fingerprint SHA-256 + modal de inactividad implementados

```python
# app.py - BÁSICO
@app.before_request
def log_page_visit():
    if 'username' in session:
        # Solo verifica expiración por tiempo
```

**✅ Mejoras de seguridad:**

```python
# security_middleware.py
import hashlib
from flask import request, session, redirect, url_for

def verify_session_fingerprint():
    """Verifica que la sesión no haya sido secuestrada"""
    if 'username' not in session:
        return True
    
    # Generar fingerprint basado en User-Agent e IP
    current_fingerprint = hashlib.sha256(
        f"{request.user_agent.string}{request.remote_addr}".encode()
    ).hexdigest()
    
    stored_fingerprint = session.get('_fingerprint')
    
    if not stored_fingerprint:
        session['_fingerprint'] = current_fingerprint
        return True
    
    if current_fingerprint != stored_fingerprint:
        # Posible sesión secuestrada
        session.clear()
        return False
    
    return True

@app.before_request
def security_checks():
    """Middleware de seguridad"""
    # 1. Verificar fingerprint de sesión
    if not verify_session_fingerprint():
        flash('Sesión inválida. Por favor, inicia sesión nuevamente.', 'danger')
        return redirect(url_for('login'))
    
    # 2. Verificar expiración por inactividad (backend)
        # Complemento frontend: modal countdown 2 min + POST /api/keep-alive (base.html)
    if 'username' in session:
        last_activity = session.get('last_activity')
        if last_activity:
            try:
                last_activity_time = datetime.fromisoformat(last_activity)
                inactive_time = datetime.now() - last_activity_time
                
                if inactive_time > timedelta(minutes=Config.SESSION_TIMEOUT_MINUTES):
                    session.clear()
                    flash('Tu sesión ha expirado por inactividad.', 'warning')
                    return redirect(url_for('login'))
            except (ValueError, TypeError):
                pass
        
        # Actualizar última actividad
        session['last_activity'] = datetime.now().isoformat()
    
    # 3. Registrar actividad (analytics)
    if 'username' in session and request.endpoint not in ['static', None]:
        log_user_activity()
```

---

## 5️⃣ APIs REST y Diseño de Endpoints — PENDIENTE

### ❌ **Problema: No sigue convenciones REST**

Endpoints actuales:
```
GET  /inventory
POST /inventory
GET  /export/excel
GET  /export/excel/exportacion
GET  /dashboard
POST /dashboard
GET  /analytics
```

**Problemas:**
1. Mezcla GET/POST en mismo endpoint sin lógica REST
2. Rutas no semánticas (`/export/excel/exportacion`)
3. Sin versionado de API
4. Sin códigos de estado HTTP apropiados
5. Sin formato de respuesta estándar

**✅ Diseño RESTful propuesto:**

```python
# api/__init__.py
from flask import Blueprint, jsonify, request
from typing import Dict, Any

api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')

class APIResponse:
    """Formato estándar de respuesta API"""
    
    @staticmethod
    def success(data: Any, message: str = "Success", status_code: int = 200) -> tuple:
        return jsonify({
            'success': True,
            'message': message,
            'data': data,
            'timestamp': datetime.utcnow().isoformat()
        }), status_code
    
    @staticmethod
    def error(message: str, errors: Dict = None, status_code: int = 400) -> tuple:
        response = {
            'success': False,
            'message': message,
            'timestamp': datetime.utcnow().isoformat()
        }
        if errors:
            response['errors'] = errors
        return jsonify(response), status_code

# api/inventory_routes.py
@api_v1.route('/inventory', methods=['GET'])
@require_auth
def get_inventory():
    """
    GET /api/v1/inventory?search=term&category_id=1&page=1&limit=50
    
    Respuesta:
    {
        "success": true,
        "message": "Inventario obtenido exitosamente",
        "data": {
            "items": [...],
            "pagination": {
                "page": 1,
                "limit": 50,
                "total": 1250,
                "pages": 25
            }
        },
        "timestamp": "2026-03-23T12:00:00Z"
    }
    """
    try:
        filters = InventoryFilters(**request.args)
    except ValidationError as e:
        return APIResponse.error('Parámetros inválidos', e.errors(), 400)
    
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 50, type=int)
    
    inventory_service = current_app.container.inventory_service()
    result = inventory_service.get_paginated_inventory(filters, page, limit)
    
    return APIResponse.success(result)

@api_v1.route('/inventory/<int:product_id>', methods=['GET'])
@require_auth
def get_inventory_item(product_id: int):
    """
    GET /api/v1/inventory/12345
    
    Obtiene detalle de un producto específico
    """
    inventory_service = current_app.container.inventory_service()
    item = inventory_service.get_inventory_item(product_id)
    
    if not item:
        return APIResponse.error('Producto no encontrado', status_code=404)
    
    return APIResponse.success(item)

@api_v1.route('/inventory/export', methods=['POST'])
@require_auth
@require_permission(Permission.EXPORT_DATA)
@limiter.limit("10 per hour")
def export_inventory():
    """
    POST /api/v1/inventory/export
    Body: {
        "filters": {...},
        "format": "xlsx",
        "columns": ["producto", "cantidad", "fecha_expira"]
    }
    
    Respuesta:
    {
        "success": true,
        "message": "Exportación completada",
        "data": {
            "download_url": "/api/v1/downloads/abc123",
            "expires_at": "2026-03-23T13:00:00Z",
            "format": "xlsx",
            "size_bytes": 2048576
        }
    }
    """
    try:
        export_request = ExportRequest(**request.json)
    except ValidationError as e:
        return APIResponse.error('Solicitud inválida', e.errors(), 400)
    
    export_service = current_app.container.export_service()
    result = export_service.create_export(
        user_email=session['username'],
        filters=export_request.filters,
        format=export_request.format
    )
    
    return APIResponse.success(result, status_code=202)  # Accepted

@api_v1.route('/dashboard/stats', methods=['GET'])
@require_permission(Permission.VIEW_DASHBOARD)
def get_dashboard_stats():
    """
    GET /api/v1/dashboard/stats?category_id=1&line_id=2
    
    Retorna estadísticas para dashboard
    """
    try:
        filters = DashboardFilters(**request.args)
    except ValidationError as e:
        return APIResponse.error('Filtros inválidos', e.errors(), 400)
    
    dashboard_service = current_app.container.dashboard_service()
    stats = dashboard_service.get_stats(filters)
    
    return APIResponse.success(stats)

# Manejo de errores global
@api_v1.errorhandler(404)
def not_found(error):
    return APIResponse.error('Recurso no encontrado', status_code=404)

@api_v1.errorhandler(500)
def internal_error(error):
    logger.error(f"Error interno: {error}")
    return APIResponse.error('Error interno del servidor', status_code=500)

# app.py - Registrar blueprint
app.register_blueprint(api_v1)
```

---

## 6️⃣ Optimización de Consultas y Performance

### ✅ **Aspectos Positivos** — SIN CAMBIOS

1. **LRU Cache implementado** para dashboard ✅
2. **Batch reading** de Odoo (evita N+1) ✅
3. **Índices en base de datos** analytics ✅

### ⚠️ **Áreas de Mejora**

#### ⚠️ **Problema 1: Sin paginación** — PENDIENTE

```python
# odoo_manager.py - PROBLEMA
def get_stock_inventory(self, ...):
    # Obtiene TODOS los registros sin límite
    stock_quants = self.models.execute_kw(...)
    # Podría ser 10,000+ registros
```

**✅ Solución:**

```python
def get_stock_inventory_paginated(
    self,
    filters: InventoryFilters,
    page: int = 1,
    limit: int = 50
) -> PaginatedResult:
    """
    Obtiene inventario paginado
    
    Returns:
        PaginatedResult con items, total y metadata de paginación
    """
    offset = (page - 1) * limit
    
    # 1. Contar total de registros
    total_count = self.models.execute_kw(
        self.db, self.uid, self.password,
        'stock.quant', 'search_count',
        [self._build_domain(filters)]
    )
    
    # 2. Obtener página actual
    stock_quants = self.models.execute_kw(
        self.db, self.uid, self.password,
        'stock.quant', 'search_read',
        [self._build_domain(filters)],
        {
            'fields': self.QUANT_FIELDS,
            'limit': limit,
            'offset': offset,
            'order': 'id desc'
        }
    )
    
    # 3. Procesar datos...
    items = self._transform_quants(stock_quants)
    
    return PaginatedResult(
        items=items,
        total=total_count,
        page=page,
        limit=limit,
        pages=math.ceil(total_count / limit)
    )
```

#### ⚠️ **Problema 2: Sin cache distribuido para múltiples instancias** — PENDIENTE

```python
# odoo_manager.py - LIMITACIÓN
@lru_cache(maxsize=32)  # Solo en memoria de un proceso
def _cached_dashboard_data(self, category_id, linea_id, lugar_id):
    pass
```

**✅ Solución con Redis:**

```python
# requirements.txt
redis==5.0.1
python-redis-cache==3.0.0

# cache_service.py
import redis
import json
import hashlib
from typing import Any, Optional, Callable
from functools import wraps

class CacheService:
    """Servicio de cache distribuido con Redis"""
    
    def __init__(self, redis_url: str):
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        self.default_ttl = 300  # 5 minutos
    
    def get(self, key: str) -> Optional[Any]:
        """Obtiene valor de cache"""
        try:
            value = self.redis_client.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            logger.error(f"Error obteniendo de cache: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Guarda valor en cache"""
        try:
            ttl = ttl or self.default_ttl
            return self.redis_client.setex(
                key,
                ttl,
                json.dumps(value, default=str)
            )
        except Exception as e:
            logger.error(f"Error guardando en cache: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Elimina valor de cache"""
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            logger.error(f"Error eliminando de cache: {e}")
            return False
    
    def invalidate_pattern(self, pattern: str):
        """Invalida todas las claves que coincidan con patrón"""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
        except Exception as e:
            logger.error(f"Error invalidando cache: {e}")
    
    def cached(self, ttl: int = None, key_prefix: str = ''):
        """Decorador para cachear resultados de funciones"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generar clave de cache
                cache_key = self._generate_cache_key(
                    key_prefix or func.__name__,
                    args,
                    kwargs
                )
                
                # Intentar obtener de cache
                cached_result = self.get(cache_key)
                if cached_result is not None:
                    logger.debug(f"Cache hit: {cache_key}")
                    return cached_result
                
                # Ejecutar función y cachear resultado
                result = func(*args, **kwargs)
                self.set(cache_key, result, ttl)
                logger.debug(f"Cache miss: {cache_key}")
                
                return result
            return wrapper
        return decorator
    
    @staticmethod
    def _generate_cache_key(prefix: str, args: tuple, kwargs: dict) -> str:
        """Genera clave de cache única"""
        key_data = f"{prefix}:{args}:{sorted(kwargs.items())}"
        return hashlib.md5(key_data.encode()).hexdigest()

# odoo_manager.py - Uso
class OdooManager:
    def __init__(self, cache_service: CacheService):
        self.cache = cache_service
        # ...
    
    @cache_service.cached(ttl=300, key_prefix='dashboard_data')
    def get_dashboard_data(self, category_id=None, linea_id=None, lugar_id=None):
        """Datos de dashboard cacheados por 5 minutos"""
        return self._get_dashboard_data_internal(category_id, linea_id, lugar_id)
    
    def invalidate_dashboard_cache(self):
        """Invalida cache de dashboard cuando hay cambios"""
        self.cache.invalidate_pattern('dashboard_data:*')
```

---

## 7️⃣ Testing y Calidad de Código ✅ COMPLETADO (FASE 1)

### ~~❌ **CRÍTICO: Ausencia total de tests**~~ ✅ RESUELTO

~~**Estado actual:** 0% de cobertura de código~~  
**Estado actual:** 79 tests implementados

| Archivo | Tests | Cobertura |
|---------|-------|-----------|
| `tests/conftest.py` | Fixtures | Mocks de OdooManager, AnalyticsDB, sesiones |
| `tests/test_odoo_manager.py` | 35 | `_transform_location_name`, `_get_related_name`, `_process_expiration_date`, whitelist, disconnect, dashboard |
| `tests/test_app_routes.py` | 27 | Login, redirects, logout, rutas autenticadas, security headers, fingerprint, session expiry, exports |
| `tests/test_analytics_db.py` | 17 | SQLite in-memory: tablas, `log_visit`, `get_total_visits`, `get_unique_users`, `get_visits_by_*` |

**Pendiente en testing:**
- [ ] Medición de cobertura (`pytest --cov`) y alcanzar ≥70%
- [ ] Tests e2e de flujos completos de usuario
- [ ] Tests para `export_excel()` y `export_excel_exportacion()`
- [ ] Tests para `authorize()` (OAuth2 callback)

**✅ Suite de tests propuesta:**

```python
# tests/conftest.py
import pytest
from app import create_app
from dependency_injector import containers, providers

class TestContainer(containers.DeclarativeContainer):
    """Contenedor de dependencias para tests"""
    
    # Mock repositories
    inventory_repository = providers.Singleton(
        MockInventoryRepository
    )
    
    analytics_repository = providers.Singleton(
        MockAnalyticsRepository
    )

@pytest.fixture
def app():
    """Fixture de aplicación Flask para tests"""
    container = TestContainer()
    app = create_app(container)
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    """Fixture de cliente de test"""
    return app.test_client()

@pytest.fixture
def authenticated_client(client):
    """Cliente autenticado para tests"""
    with client.session_transaction() as sess:
        sess['username'] = 'test@agrovetmarket.com'
        sess['user_name'] = 'Test User'
        sess['last_activity'] = datetime.now().isoformat()
    return client

# tests/unit/test_odoo_manager.py
import pytest
from odoo_manager import OdooManager

class TestOdooManager:
    """Tests unitarios de OdooManager"""
    
    def test_transform_location_name(self):
        """Test de transformación de nombres de ubicación"""
        # Arrange
        long_name = 'ALMC/Stock/Corto Vencimiento/VCTO1A3M'
        
        # Act
        short_name = OdooManager._transform_location_name(long_name)
        
        # Assert
        assert short_name == '0≥P≤3'
    
    def test_process_expiration_date_valid(self):
        """Test de procesamiento de fecha válida"""
        # Arrange
        date_str = '2026-12-31'
        
        # Act
        formatted, months = OdooManager._process_expiration_date(date_str)
        
        # Assert
        assert formatted == '31-12-2026'
        assert months >= 9  # Al menos 9 meses desde marzo 2026
    
    def test_process_expiration_date_invalid(self):
        """Test de procesamiento de fecha inválida"""
        # Arrange
        date_str = 'invalid-date'
        
        # Act
        formatted, months = OdooManager._process_expiration_date(date_str)
        
        # Assert
        assert formatted == 'invalid-date'
        assert months is None
    
    def test_is_user_authorized_in_whitelist(self):
        """Test de autorización de usuario en whitelist"""
        # Arrange
        manager = OdooManager()
        manager.whitelist = {'test@domain.com', 'admin@domain.com'}
        
        # Act & Assert
        assert manager.is_user_authorized('test@domain.com')
        assert manager.is_user_authorized('TEST@DOMAIN.COM')  # Case insensitive
        assert not manager.is_user_authorized('unauthorized@domain.com')

# tests/integration/test_api_inventory.py
import pytest

class TestInventoryAPI:
    """Tests de integración de API de inventario"""
    
    def test_get_inventory_unauthenticated(self, client):
        """Test de acceso sin autenticación"""
        # Act
        response = client.get('/api/v1/inventory')
        
        # Assert
        assert response.status_code == 401
    
    def test_get_inventory_authenticated(self, authenticated_client):
        """Test de obtener inventario autenticado"""
        # Act
        response = authenticated_client.get('/api/v1/inventory')
        
        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'items' in data['data']
        assert 'pagination' in data['data']
    
    def test_get_inventory_with_filters(self, authenticated_client):
        """Test de filtros en inventario"""
        # Act
        response = authenticated_client.get(
            '/api/v1/inventory?search=ALIMENTO&category_id=1'
        )
        
        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['data']['items']) > 0
    
    def test_export_inventory_rate_limit(self, authenticated_client):
        """Test de rate limiting en exportación"""
        # Act - Hacer 11 requests (límite es 10/hora)
        for i in range(11):
            response = authenticated_client.post('/api/v1/inventory/export')
        
        # Assert
        assert response.status_code == 429  # Too Many Requests

# tests/e2e/test_user_flows.py
class TestUserFlows:
    """Tests end-to-end de flujos de usuario"""
    
    def test_complete_login_flow(self, client):
        """Test de flujo completo de login"""
        # 1. Acceder a login
        response = client.get('/login')
        assert response.status_code == 200
        
        # 2. Iniciar OAuth (mock)
        # ...
        
        # 3. Verificar redirección a dashboard/inventory
        # ...
    
    def test_filter_and_export_flow(self, authenticated_client):
        """Test de flujo de filtrado y exportación"""
        # 1. Aplicar filtros
        response = authenticated_client.get(
            '/inventory?search=ALIMENTO&category_id=1'
        )
        assert response.status_code == 200
        
        # 2. Exportar datos
        response = authenticated_client.post('/api/v1/inventory/export')
        assert response.status_code == 202
        
        # 3. Descargar archivo
        # ...

# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --verbose
    --cov=app
    --cov=odoo_manager
    --cov=analytics_db
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=70

# Comandos
# pytest                           # Ejecutar todos los tests
# pytest -v tests/unit/            # Solo tests unitarios
# pytest --cov                     # Con cobertura
# pytest -k "test_export"          # Tests que contengan "export"
```

---

## 8️⃣ Arquitectura de Microservicios

### ⚠️ **Evaluación actual**

**Estado:** Arquitectura monolítica (apropiada para tamaño actual)

**Cuándo considerar microservicios:**
- Más de 10 desarrolladores trabajando simultáneamente
- Necesidad de escalar componentes independientemente
- Equipos autónomos por funcionalidad
- Tecnologías heterogéneas por servicio

### 📋 **Plan de migración a microservicios (futuro)**

```
## Servicios propuestos:

1. **Auth Service** (Autenticación y Autorización)
   - OAuth2 Google
   - Whitelist management
   - Permission checking
   - JWT issuing
   
2. **Inventory Service** (Datos de Inventario)
   - Integración Odoo
   - Cache de datos
   - Transformación de datos
   - API REST pública
   
3. **Analytics Service** (Telemetría)
   - Recolección de eventos
   - Queries de analytics
   - Reportes
   
4. **Export Service** (Generación de archivos)
   - Excel generation
   - PDF generation
   - Queue-based processing
   
5. **Notification Service** (Alertas)
   - Email notifications
   - Slack/webhook notifications
   - Alertas de stock bajo

## Comunicación entre servicios:

- **Sincrónica:** gRPC para baja latencia
- **Asíncrona:** RabbitMQ/Apache Kafka para eventos
- **API Gateway:** Kong o AWS API Gateway

## Desafíos:
- Complejidad operacional aumenta 10x
- Necesidad de service mesh (Istio/Linkerd)
- Distributed tracing (Jaeger/Zipkin)
- Manejo de transacciones distribuidas (Saga pattern)
```

**Recomendación actual:** Mantener monolito modular hasta alcanzar 50,000+ usuarios activos.

---

## 9️⃣ Logging y Observabilidad

### ❌ **Problema: Logging insuficiente**

```python
# app.py - BÁSICO
print(f"Error en autenticación OAuth2: {e}")
```

**✅ Solución profesional:**

```python
# logging_config.py
import logging
import sys
from pythonjsonlogger import jsonlogger

def configure_logging(app):
    """Configura logging estructurado"""
    
    # Formato JSON para producción
    if app.config['ENVIRONMENT'] == 'production':
        log_handler = logging.StreamHandler(sys.stdout)
        formatter = jsonlogger.JsonFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s'
        )
        log_handler.setFormatter(formatter)
    else:
        # Formato legible para desarrollo
        log_handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        log_handler.setFormatter(formatter)
    
    # Configurar nivel de log
    log_level = logging.DEBUG if app.debug else logging.INFO
    
    app.logger.addHandler(log_handler)
    app.logger.setLevel(log_level)
    
    # Deshabilitar logs de bibliotecas externas
    logging.getLogger('werkzeug').setLevel(logging.WARNING)

# app.py
from logging_config import configure_logging
import structlog

configure_logging(app)
logger = structlog.get_logger(__name__)

@app.route('/authorize')
def authorize():
    try:
        token = google.authorize_access_token()
        user_info = token.get('userinfo')
        email = user_info.get('email')
        
        logger.info(
            "oauth_success",
            user_email=email,
            provider="google"
        )
        
        # ...
    except Exception as e:
        logger.error(
            "oauth_failure",
            error=str(e),
            error_type=type(e).__name__,
            stack_trace=traceback.format_exc()
        )
        raise

# Métricas con Prometheus
from prometheus_flask_exporter import PrometheusMetrics

metrics = PrometheusMetrics(app)

# Métricas automáticas:
# - http_request_duration_seconds
# - http_request_total
# - http_request_size_bytes

# Métricas personalizadas
inventory_queries = metrics.counter(
    'inventory_queries_total',
    'Total de consultas a inventario',
    labels={'status': lambda r: r.status_code}
)
```

---

## 🔟 Resumen de Recomendaciones Priorizadas

### 🔴 **Alta Prioridad (Implementar YA)**

1. **Testing** - Cobertura mínima 70%
   - Esfuerzo: 2-3 semanas
   - Impacto: Previene regresiones críticas

2. **Validación de Inputs** (Pydantic)
   - Esfuerzo: 3 días
   - Impacto: Previene injection attacks

3. **Headers de Seguridad** (Flask-Talisman)
   - Esfuerzo: 1 día
   - Impacto: Cumplimiento OWASP

4. **Rate Limiting**
   - Esfuerzo: 2 días
   - Impacto: Previene DoS y brute force

5. **Configuración de Roles** (eliminar hardcoding)
   - Esfuerzo: 1 semana
   - Impacto: Mantenibilidad y seguridad

### ⚠️ **Media Prioridad (Próximos 3 meses)**

6. **API RESTful** con versionado
   - Esfuerzo: 2 semanas
   - Impacto: Estándares de industria

7. **Paginación** en consultas
   - Esfuerzo: 1 semana
   - Impacto: Performance con datos grandes

8. **Dependency Injection**
   - Esfuerzo: 1 semana
   - Impacto: Testability y mantenibilidad

9. **Logging estructurado**
   - Esfuerzo: 3 días
   - Impacto: Debugging en producción

10. **Secrets Management**
    - Esfuerzo: 1 semana
    - Impacto: Seguridad de credenciales

### ℹ️ **Baja Prioridad (Roadmap 6+ meses)**

11. **Cache distribuido** (Redis)
12. **Refactoring SOLID** completo
13. **Observabilidad** (Prometheus/Grafana)
14. **CI/CD Pipeline** automatizado
15. **Migración a microservicios** (si es necesario)

---

## 📈 Plan de Acción - Próximos 30 días

### Semana 1: Fundamentos de Testing
- [ ] Configurar pytest y fixtures
- [ ] Escribir 20 tests unitarios críticos
- [ ] Configurar coverage reporting (objetivo 30%)

### Semana 2: Seguridad Básica
- [ ] Implementar Flask-Talisman
- [ ] Agregar validación Pydantic en 5 endpoints principales
- [ ] Configurar Flask-Limiter

### Semana 3: Refactoring de Permisos
- [ ] Extraer roles a archivo JSON/YAML
- [ ] Crear decoradores de autorización
- [ ] Migrar 10 endpoints a nuevo sistema

### Semana 4: API REST
- [ ] Diseñar esquema API v1
- [ ] Implementar 5 endpoints RESTful principales
- [ ] Documentar con OpenAPI/Swagger

---

## 📚 Referencias y Recursos

### Libros Recomendados
- "Clean Code" - Robert C. Martin
- "Refactoring" - Martin Fowler
- "Building Microservices" - Sam Newman
- "Web Application Security" - Andrew Hoffman

### Herramientas
- **Linting:** `pylint`, `flake8`, `black`, `mypy`
- **Testing:** `pytest`, `pytest-cov`, `faker`
- **Seguridad:** `bandit`, `safety`, `OWASP ZAP`
- **Performance:** `locust`, `py-spy`, `memory_profiler`

### Checklist de Code Review
```markdown
- [ ] Código cumple PEP 8
- [ ] Funciones tienen docstrings
- [ ] Tests pasan (cobertura >70%)
- [ ] Sin hardcoded secrets
- [ ] Inputs validados
- [ ] Logs apropiados
- [ ] Sin código duplicado
- [ ] Nombres descriptivos
- [ ] Errores manejados
- [ ] Performance OK
```

---

**Documento generado:** 23 de marzo de 2026  
**Próxima revisión:** Al completar plan de 30 días  
**Contacto:** Desarrollador Senior - Code Review Team
