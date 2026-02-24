# Inventario Stock Web

Sistema web para visualización de inventario de stock desde Odoo.

## Características

- 🔐 **Autenticación con lista blanca**: Control de acceso basado en emails autorizados
- 📊 **Dashboard interactivo**: 6 gráficos con datos en tiempo real
- 🔍 **Filtros avanzados**: Por línea comercial, categoría, ubicación y búsqueda libre
- 📤 **Exportación a Excel**: Descarga reportes con los datos filtrados
- 🎨 **Código de colores**: Identificación visual de productos por vencimiento
- ⚡ **Datos en tiempo real**: Conexión directa con Odoo XML-RPC
- 📈 **Sistema de Analytics**: Monitoreo de visitas y análisis de uso (solo admins)

## Requisitos

- Python 3.8+
- Odoo 14+ con acceso XML-RPC
- Credenciales de usuario con permisos de lectura en stock

## Instalación Local

1. **Clonar el repositorio**
```bash
git clone https://github.com/jonathancerda-hub/inventario-stock-web.git
cd inventario-stock-web
```

2. **Crear entorno virtual**
```bash
python -m venv venv
```

3. **Activar entorno virtual**
- Windows PowerShell:
```powershell
.\venv\Scripts\Activate.ps1
```
- Linux/Mac:
```bash
source venv/bin/activate
```

4. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

5. **Configurar variables de entorno**

Crea un archivo `.env` en la raíz del proyecto:
```env
ODOO_URL=https://tu-odoo-instance.com
ODOO_DB=nombre_base_datos
ODOO_USER=usuario_admin
ODOO_PASSWORD=contraseña_segura
```

6. **Configurar lista blanca de usuarios**

Copia el archivo de ejemplo y edítalo con los emails autorizados:
```bash
cp whitelist.txt.example whitelist.txt
```

Edita `whitelist.txt` y agrega los emails (uno por línea):
```
usuario1@empresa.com
usuario2@empresa.com
```

7. **Ejecutar la aplicación**
```bash
python app.py
```

La aplicación estará disponible en `http://localhost:5000`

## Despliegue en Render

### 1. Configurar Variables de Entorno

En Render Dashboard > Environment, agrega estas variables:

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `ODOO_URL` | URL de tu instancia Odoo | `https://odoo.empresa.com` |
| `ODOO_DB` | Nombre de la base de datos | `produccion` |
| `ODOO_USER` | Usuario con acceso a stock | `admin` |
| `ODOO_PASSWORD` | Contraseña del usuario | `contraseña123` |
| `WHITELIST_EMAILS` | Lista de emails autorizados (separados por comas) | Ver abajo |
| `DATABASE_URL` | Conexión PostgreSQL de Supabase (para analytics) | Ver [SUPABASE_SETUP.md](SUPABASE_SETUP.md) |

### 2. Generar WHITELIST_EMAILS

Ejecuta este comando en local para generar el string de emails:

```bash
python generate_whitelist_env.py
```

Copia la salida y pégala como valor de la variable `WHITELIST_EMAILS` en Render.

O copia directamente todos los emails separados por comas:
```
user1@empresa.com,user2@empresa.com,user3@empresa.com
```

### 3. Conectar Repositorio

1. En Render, crea un nuevo **Web Service**
2. Conecta tu repositorio de GitHub
3. Configuración:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
4. Agrega las variables de entorno (paso 1)
5. Deploy

### 4. Actualizar la Whitelist

Para agregar o remover usuarios sin redesplegar:

1. Ve a Render Dashboard > Environment
2. Edita la variable `WHITELIST_EMAILS`
3. Agrega/remueve emails (separados por comas)
4. Save Changes (Render reiniciará automáticamente)

**Ver más detalles en:** [RENDER_SETUP.md](RENDER_SETUP.md)

## Sistema de Autenticación

El sistema usa **doble capa de seguridad**:

1. ✅ **Verificación de lista blanca**: El email debe estar en `WHITELIST_EMAILS` o `whitelist.txt`
2. ✅ **Autenticación Odoo**: Las credenciales deben ser válidas en Odoo

### Mensajes de Error

- **"Acceso denegado. Usuario no autorizado"** → Email no está en la lista blanca
- **"Usuario o contraseña incorrectos"** → Credenciales de Odoo inválidas

## Sistema de Analytics

El sistema incluye **monitoreo avanzado de visitas** con almacenamiento en **Supabase PostgreSQL**.

### Características

- 📊 **Métricas en tiempo real**: Total de visitas, usuarios únicos, visitas por página
- 📈 **Gráficos interactivos**: Visitas por día, visitas por hora, top usuarios
- 🔍 **Detalles granulares**: IP, user agent, referrer, method HTTP
- 🔐 **Solo para admins**: Acceso restringido a usuarios autorizados
- 💾 **Persistencia garantizada**: Datos almacenados en Supabase PostgreSQL
- 🗄️ **Base de datos exclusiva**: Supabase dedicado solo a este proyecto

### Configuración

1. ✅ **Tabla creada**: `page_visits` en Supabase
2. 📝 **Ver setup completo**: [SUPABASE_SETUP.md](SUPABASE_SETUP.md)
3. 🔧 **Variable requerida**: `DATABASE_URL` en Render Environment

### Exclusión de Rastreo

Los siguientes emails **no generan registros** en analytics:
- `jonathan.cerda@agrovetmarket.com`

Para agregar más exclusiones, edita `ADMIN_ANALYTICS_EMAILS` en [analytics_db.py](analytics_db.py).

## Estructura del Proyecto

```
inventario-stock/
├── app.py                      # Aplicación Flask principal
├── odoo_manager.py             # Lógica de conexión y consultas Odoo
├── conectar_odoo.py            # Script de prueba de conexión
├── generate_whitelist_env.py   # Generador de string para Render
├── requirements.txt            # Dependencias Python
├── .env                        # Variables de entorno (local, git-ignored)
├── whitelist.txt              # Lista de emails autorizados (local, git-ignored)
├── whitelist.txt.example      # Plantilla de whitelist
├── .gitignore                 # Archivos ignorados por git
├── templates/                 # Plantillas HTML
│   ├── base.html
│   ├── login.html
│   ├── inventory.html
│   ├── dashboard.html
│   └── export_inventory.html
├── static/                    # Archivos estáticos
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
├── manual_usuario.html        # Manual de usuario completo
├── PRD.html                   # Documento de requerimientos del producto
└── RENDER_SETUP.md           # Guía de configuración para Render
```

## Documentación

- 📖 **Manual de Usuario**: `manual_usuario.html` - Guía completa para usuarios finales
- 📋 **PRD**: `PRD.html` - Product Requirements Document con arquitectura y features
- 🚀 **Setup Render**: `RENDER_SETUP.md` - Configuración detallada para despliegue
- 📊 **Setup Supabase**: `SUPABASE_SETUP.md` - Configuración de analytics con Supabase PostgreSQL
- 📈 **Sistema Analytics**: `SISTEMA_ANALYTICS.md` - Documentación del sistema de monitoreo

## Características Técnicas

### Dashboard

- **KPIs**: Total productos, cantidad total, unidades por vencer (0-3 meses)
- **Gráficos interactivos**:
  1. Top 5 productos por stock
  2. Distribución por rango de vencimiento (dona)
  3. Productos críticos por línea comercial
  4. Top 5 productos por vencer
  5. Stock por categoría
  6. Stock por línea comercial

### Código de Colores

| Color | Rango | Estado |
|-------|-------|--------|
| 🔴 Rojo | 0-3 meses | Crítico |
| 🟠 Ámbar | 3-6 meses | Advertencia |
| 🟡 Amarillo | 6-9 meses | Precaución |
| ⚪ Gris | 9-12 meses | Estable |
| 🟢 Verde | >12 meses | Óptimo |

### Filtros Disponibles

- **Línea Comercial**: Filtra por línea de productos
- **Grupo Artículo**: Filtra por categoría
- **Lugar**: Filtra por ubicación de almacén
- **Búsqueda libre**: Busca por código, nombre o lote

## Comandos Útiles

### Desarrollo Local

```bash
# Activar entorno virtual
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate      # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación
python app.py

# Generar string de whitelist para Render
python generate_whitelist_env.py

# Probar conexión con Odoo
python conectar_odoo.py
```

### Git

```bash
# Ver cambios
git status

# Agregar cambios
git add .

# Commit
git commit -m "descripción del cambio"

# Push a GitHub
git push origin main
```

## Soporte

Para reportar problemas o solicitar nuevas funcionalidades:

- **Product Owner**: jonathan.cerda@agrovetmarket.com
- **GitHub Issues**: [inventario-stock-web/issues](https://github.com/jonathancerda-hub/inventario-stock-web/issues)

## Licencia

© 2025 AgrovetMarket - Uso interno
