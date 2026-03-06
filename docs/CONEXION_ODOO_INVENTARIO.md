# Guía de Conexión a Odoo y Tabla de Inventario

## 📋 Tabla de Contenidos
1. [Configuración de Conexión](#configuración-de-conexión)
2. [Autenticación XML-RPC](#autenticación-xml-rpc)
3. [Estructura de OdooManager](#estructura-de-odoomanager)
4. [Obtención de Datos de Inventario](#obtención-de-datos-de-inventario)
5. [Procesamiento de Datos](#procesamiento-de-datos)
6. [Estructura de la Tabla de Inventario](#estructura-de-la-tabla-de-inventario)
7. [Ejemplos de Uso](#ejemplos-de-uso)

---

## Configuración de Conexión

### Variables de Entorno Requeridas

En el archivo `.env` del proyecto, se deben configurar las siguientes credenciales de Odoo:

```env
# Configuración de Odoo
ODOO_URL=https://agrovetmarket-main-7338015.dev.odoo.com
ODOO_DB=agrovetmarket-main-7338015
ODOO_USER=admin
ODOO_PASSWORD=admin
```

### Descripción de Variables

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `ODOO_URL` | URL base de la instancia de Odoo | `https://agrovetmarket-main-7338015.dev.odoo.com` |
| `ODOO_DB` | Nombre de la base de datos de Odoo | `agrovetmarket-main-7338015` |
| `ODOO_USER` | Usuario con permisos de lectura | `admin` |
| `ODOO_PASSWORD` | Contraseña del usuario | `admin` |

⚠️ **Nota de Seguridad**: Nunca incluir estas credenciales en el control de versiones. Usar `.env` y asegurar que esté en `.gitignore`.

---

## Autenticación XML-RPC

### Proceso de Conexión

El sistema utiliza **XML-RPC** para conectarse a Odoo. Esta es la tecnología estándar de comunicación con la API de Odoo.

#### Inicialización en OdooManager

```python
def __init__(self):
    # Cargar credenciales desde variables de entorno
    self.url = os.getenv('ODOO_URL')
    self.db = os.getenv('ODOO_DB')
    self.user = os.getenv('ODOO_USER')
    self.password = os.getenv('ODOO_PASSWORD')
    
    # Endpoints XML-RPC
    common_url = f'{self.url}/xmlrpc/2/common'
    models_url = f'{self.url}/xmlrpc/2/object'
    
    # Autenticar y obtener UID
    common = xmlrpc.client.ServerProxy(common_url)
    self.uid = common.authenticate(self.db, self.user, self.password, {})
    
    if self.uid:
        # Conectar al endpoint de modelos para consultas
        self.models = xmlrpc.client.ServerProxy(models_url)
        self.is_connected = True
        print("✅ Conexión a Odoo establecida")
    else:
        print("❌ Error de autenticación en Odoo")
```

### Endpoints XML-RPC de Odoo

1. **`/xmlrpc/2/common`**: Autenticación y metadatos
   - Método: `authenticate(db, user, password, {})`
   - Retorna: `uid` (User ID) si la autenticación es exitosa

2. **`/xmlrpc/2/object`**: Operaciones CRUD en modelos
   - Métodos: `search`, `read`, `search_read`, `create`, `write`, `unlink`

---

## Estructura de OdooManager

### Clase Principal: `OdooManager`

Ubicada en `odoo_manager.py`, esta clase gestiona todas las operaciones con Odoo.

#### Propiedades

```python
class OdooManager:
    def __init__(self):
        self.url: str           # URL de Odoo
        self.db: str            # Base de datos
        self.user: str          # Usuario
        self.password: str      # Contraseña
        self.uid: int           # User ID autenticado
        self.models: ServerProxy # Proxy para operaciones de modelos
        self.is_connected: bool  # Estado de conexión
        self.whitelist: set     # Usuarios autorizados
```

#### Métodos Principales

| Método | Descripción |
|--------|-------------|
| `get_stock_inventory()` | Obtiene inventario nacional con filtros |
| `get_export_inventory()` | Obtiene inventario de exportación |
| `get_dashboard_data()` | Calcula KPIs y estadísticas para dashboard |
| `get_lineas_comerciales()` | Lista líneas comerciales disponibles |
| `get_grupos_articulos()` | Lista categorías de productos |
| `get_lugares()` | Lista ubicaciones de almacén |

---

## Obtención de Datos de Inventario

### Modelo de Odoo: `stock.quant`

El inventario se obtiene consultando el modelo **`stock.quant`** de Odoo, que representa los _quants_ (unidades de stock en ubicaciones específicas).

### Método: `get_stock_inventory()`

#### Parámetros

```python
def get_stock_inventory(
    search_term=None,      # Término de búsqueda (código/nombre/lote)
    grupo_id=None,         # ID de categoría de producto
    linea_id=None,         # ID de línea comercial
    lugar_id=None,         # ID de ubicación
    product_id=None        # ID específico de producto
)
```

#### Dominio de Filtros

```python
domain = [
    ('location_id.usage', '=', 'internal'),          # Ubicaciones internas
    ('location_id', 'child_of', 'ALMC/Stock')        # Hijos de ALMC/Stock
]

# Filtros opcionales
if grupo_id:
    domain.append(('product_id.categ_id', '=', grupo_id))
if linea_id:
    domain.append(('product_id.commercial_line_national_id', '=', linea_id))
if lugar_id:
    domain.append(('location_id', '=', lugar_id))
if search_term:
    search_domain = [
        '|', ('product_id.default_code', 'ilike', search_term),
        '|', ('product_id.name', 'ilike', search_term),
        ('lot_id.name', 'ilike', search_term)
    ]
    domain.extend(search_domain)
```

#### Consulta a Odoo

```python
# 1. Obtener stock quants con filtros
quant_fields = ['product_id', 'available_quantity', 'lot_id', 'location_id']
stock_quants = self.models.execute_kw(
    self.db, self.uid, self.password,
    'stock.quant',           # Modelo
    'search_read',           # Método
    [domain],                # Dominio de filtros
    {'fields': quant_fields} # Campos a obtener
)

# 2. Obtener detalles de productos
product_ids = [quant['product_id'][0] for quant in stock_quants]
product_fields = ['display_name', 'default_code', 'categ_id', 'commercial_line_national_id']
product_details = self.models.execute_kw(
    self.db, self.uid, self.password,
    'product.product',
    'read',
    [product_ids],
    {'fields': product_fields, 'context': {'lang': 'es_PE'}}
)

# 3. Obtener fechas de expiración de lotes
lot_ids = [quant['lot_id'][0] for quant in stock_quants if quant.get('lot_id')]
lot_details = self.models.execute_kw(
    self.db, self.uid, self.password,
    'stock.lot',
    'read',
    [lot_ids],
    {'fields': ['expiration_date']}
)
```

---

## Procesamiento de Datos

### Cálculo de Meses de Expiración

```python
@staticmethod
def _process_expiration_date(exp_date_str):
    """Procesa una cadena de fecha de expiración y calcula los meses restantes."""
    if not exp_date_str:
        return '', None
    
    try:
        # Parsear fecha de Odoo (formato: 'YYYY-MM-DD HH:MM:SS')
        date_part = exp_date_str.split(' ')[0]
        exp_date_obj = datetime.strptime(date_part, '%Y-%m-%d')
        
        # Formato legible para el usuario (DD-MM-YYYY)
        formatted_exp_date = exp_date_obj.strftime('%d-%m-%Y')
        
        # Calcular meses hasta expiración
        today = datetime.now()
        months_to_expire = (exp_date_obj.year - today.year) * 12 + \
                          (exp_date_obj.month - today.month)
        
        return formatted_exp_date, months_to_expire
    except (ValueError, TypeError):
        return exp_date_str, None
```

### Transformación de Nombres de Ubicaciones

```python
@staticmethod
def _transform_location_name(location_name):
    """Convierte nombres técnicos de ubicación a abreviaturas legibles."""
    transformations = {
        'ALMC/Stock/Corto Vencimiento/VCTO1A3M': '0≥P≤3',
        'ALMC/Stock/Corto Vencimiento/VCTO3A6M': '3>P<6',
        'ALMC/Stock/Corto Vencimiento/VCTO6A9M': '6≥P<9',
        'ALMC/Stock/Corto Vencimiento/VCTO9A12M': '9≥P≤12',
        'ALMC/Stock/Comercial': 'P≥12'
    }
    return transformations.get(location_name, location_name)
```

### Construcción del Item de Inventario

```python
inventory_item = {
    'product_id': prod_id,
    'grupo_articulo_id': product_data.get('categ_id', [0, ''])[0],
    'grupo_articulo': self._get_related_name(product_data.get('categ_id')),
    'linea_comercial': self._get_related_name(product_data.get('commercial_line_national_id')),
    'cod_articulo': product_data.get('default_code', ''),
    'producto': product_data.get('display_name', ''),
    'lugar': self._transform_location_name(self._get_related_name(quant.get('location_id'))),
    'fecha_expira': formatted_exp_date,
    'cantidad_disponible': f"{quant.get('available_quantity', 0):,.2f}",
    'meses_expira': months_to_expire
}
```

---

## Estructura de la Tabla de Inventario

### Campos del Inventario

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `product_id` | int | ID interno del producto en Odoo | `12345` |
| `grupo_articulo_id` | int | ID de categoría del producto | `67` |
| `grupo_articulo` | str | Nombre de la categoría | `PCV - INSTRUMENTAL` |
| `linea_comercial` | str | Línea comercial del producto | `OTROS` |
| `cod_articulo` | str | Código SKU del producto | `33000PER00733` |
| `producto` | str | Nombre completo del producto con variantes | `[33000PER00733] ARETE ALFATAG OVINO/CAPRINO 38 X 36 MM + BOTON NARANJA X 25 UND` |
| `lugar` | str | Ubicación abreviada en almacén | `P≥12` |
| `fecha_expira` | str | Fecha de expiración (DD-MM-YYYY) | `15-06-2026` |
| `cantidad_disponible` | str | Cantidad con formato de comas | `430.00` |
| `meses_expira` | int/None | Meses hasta expiración | `3` o `None` |

### Coloración por Estado de Expiración

En `templates/inventory.html`, los valores de `meses_expira` se colorean automáticamente:

| Rango (meses) | Clase CSS | Color | Estado |
|---------------|-----------|-------|--------|
| 0 - 3 | `status-red` | Rojo | Crítico |
| 3 - 6 | `status-amber` | Ámbar | Advertencia |
| 6 - 9 | `status-yellow` | Amarillo | Precaución |
| 9 - 12 | `status-grey` | Gris | Normal |
| > 12 | `status-green` | Verde | Óptimo |

### Ordenamiento de Tabla

La tabla de inventario se ordena por defecto por `meses_expira` ascendente (productos próximos a vencer primero).

```python
inventory_list.sort(
    key=lambda item: item['meses_expira'] if item['meses_expira'] is not None else float('inf')
)
```

### Funcionalidad de Doble Clic para Ordenar

Los usuarios pueden hacer **doble clic** en cualquier cabecera de columna para ordenar:

- **Columna Producto**: Ordena por nombre (ignora el código entre corchetes)
- **Columnas de Cantidad/Meses**: Ordena numéricamente
- **Fecha Expira**: Ordena por fecha (convierte DD-MM-YYYY correctamente)
- **Otras columnas**: Ordena alfabéticamente (case-insensitive)

---

## Ejemplos de Uso

### Ejemplo 1: Obtener Todo el Inventario

```python
from odoo_manager import OdooManager

# Inicializar manager
manager = OdooManager()

# Obtener inventario completo
inventory = manager.get_stock_inventory()

# Imprimir primeros 5 productos
for item in inventory[:5]:
    print(f"{item['cod_articulo']}: {item['producto']} - Cantidad: {item['cantidad_disponible']}")
```

### Ejemplo 2: Filtrar por Línea Comercial

```python
# Obtener líneas comerciales disponibles
lineas = manager.get_lineas_comerciales()
print(f"Líneas disponibles: {lineas}")

# Filtrar inventario por línea específica
linea_id = 23  # ID de la línea "OTROS"
inventory_otros = manager.get_stock_inventory(linea_id=linea_id)
print(f"Productos en línea OTROS: {len(inventory_otros)}")
```

### Ejemplo 3: Buscar Productos por Término

```python
# Buscar productos que contengan "ARETE"
inventory_aretes = manager.get_stock_inventory(search_term="ARETE")

for item in inventory_aretes:
    print(f"{item['producto']} - Ubicación: {item['lugar']} - Expira: {item['fecha_expira']}")
```

### Ejemplo 4: Productos Próximos a Vencer

```python
# Obtener inventario y filtrar por meses de expiración
inventory = manager.get_stock_inventory()

# Productos con expiración entre 0-3 meses
proximos_vencer = [
    item for item in inventory 
    if item['meses_expira'] is not None and 0 <= item['meses_expira'] <= 3
]

print(f"Productos críticos (0-3 meses): {len(proximos_vencer)}")
for item in proximos_vencer[:10]:
    print(f"⚠️ {item['producto']}: Expira en {item['meses_expira']} meses ({item['fecha_expira']})")
```

### Ejemplo 5: Datos para Dashboard

```python
# Obtener KPIs y estadísticas para el dashboard
dashboard_data = manager.get_dashboard_data(
    category_id=None,  # Todas las categorías
    linea_id=None,     # Todas las líneas
    lugar_id=None      # Todos los lugares
)

print(f"Total productos: {dashboard_data['kpi_total_products']}")
print(f"Cantidad total: {dashboard_data['kpi_total_quantity']}")
print(f"Productos por vencer pronto: {dashboard_data['kpi_vence_pronto']}")

# Top 5 productos con más stock
for label, data_dict in zip(dashboard_data['chart_labels'], dashboard_data['chart_data']):
    print(f"  {label}: {data_dict} unidades")
```

---

## Solución de Problemas

### Error: "Error de autenticación en Odoo"

**Causa**: Credenciales incorrectas en `.env`

**Solución**: 
1. Verificar que `ODOO_URL`, `ODOO_DB`, `ODOO_USER` y `ODOO_PASSWORD` sean correctos
2. Probar autenticación manualmente con las credenciales
3. Verificar que el usuario tenga permisos de lectura en `stock.quant`, `product.product` y `stock.lot`

### Error: "list index out of range" en product_id

**Causa**: El campo `product_id` en Odoo devuelve un array `[id, 'Nombre']` pero está vacío

**Solución**: Agregar validación:
```python
if quant.get('product_id'):
    prod_id = quant['product_id'][0]
else:
    continue  # Saltar este quant
```

### Error: "KeyError: 'available_quantity'"

**Causa**: El campo `available_quantity` no existe en la versión de Odoo

**Solución**: Verificar campos disponibles con:
```python
fields = self.models.execute_kw(
    self.db, self.uid, self.password,
    'stock.quant', 'fields_get', [],
    {'attributes': ['string', 'type']}
)
print(fields.keys())
```

---

## Contacto y Soporte

Para preguntas sobre la conexión a Odoo o estructura de datos:

- **Desarrollador**: Jonathan Cerda
- **Email**: jonathan.cerda@agrovetmarket.com
- **Repositorio**: [inventario-stock-web](https://github.com/jonathancerda-hub/inventario-stock-web)

---

**Última actualización**: 4 de marzo de 2026
