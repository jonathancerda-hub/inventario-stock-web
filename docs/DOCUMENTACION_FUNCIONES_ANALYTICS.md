# 📊 Documentación del Sistema de Analytics

## 📋 Descripción General

Sistema completo de monitoreo y análisis de visitas para dashboards web. Permite rastrear el uso del sistema, analizar patrones de comportamiento de usuarios y generar reportes estadísticos detallados.

## 🏗️ Arquitectura

### Tecnologías Utilizadas
- **Backend**: Python con Flask
- **Base de Datos**: PostgreSQL (producción) / SQLite (desarrollo)
- **Frontend**: HTML/CSS/JavaScript con Google Charts
- **Gestión de Timezone**: PyTZ (Zona horaria de Perú)

### Estructura de Archivos
```
├── analytics_db.py          # Clase principal de gestión de analytics
├── app.py                   # Rutas y endpoints de Flask
└── templates/
    └── analytics.html       # Interfaz de visualización
```

---

## 🔧 Clase AnalyticsDB

### Constructor
```python
def __init__(self)
```
**Descripción**: Inicializa la conexión a la base de datos y crea las tablas necesarias.

**Características**:
- Detección automática del entorno (desarrollo/producción)
- Fallback a SQLite si PostgreSQL no está disponible
- Configuración de timezone (America/Lima)

### Métodos Principales

#### 1. log_visit()
```python
def log_visit(self, user_email, user_name, page_url, page_title=None, 
              ip_address=None, user_agent=None, referrer=None, method='GET')
```
**Descripción**: Registra una visita de usuario a una página.

**Parámetros**:
- `user_email` (str): Email del usuario
- `user_name` (str): Nombre del usuario
- `page_url` (str): URL de la página visitada
- `page_title` (str, opcional): Título de la página
- `ip_address` (str, opcional): Dirección IP del usuario
- `user_agent` (str, opcional): User-Agent del navegador
- `referrer` (str, opcional): URL de referencia
- `method` (str, opcional): Método HTTP (default: 'GET')

**Uso**:
```python
analytics_db.log_visit(
    user_email='usuario@ejemplo.com',
    user_name='Juan Pérez',
    page_url='/dashboard',
    page_title='Dashboard Principal',
    ip_address='192.168.1.1'
)
```

---

#### 2. get_total_visits()
```python
def get_total_visits(self, days=30)
```
**Descripción**: Obtiene el número total de visitas en un período determinado.

**Parámetros**:
- `days` (int): Número de días hacia atrás (default: 30)

**Retorna**: `int` - Total de visitas

**Ejemplo**:
```python
total = analytics_db.get_total_visits(days=7)  # Visitas de los últimos 7 días
```

---

#### 3. get_unique_users()
```python
def get_unique_users(self, days=30)
```
**Descripción**: Obtiene el número de usuarios únicos en un período.

**Parámetros**:
- `days` (int): Número de días hacia atrás (default: 30)

**Retorna**: `int` - Número de usuarios únicos

**Ejemplo**:
```python
usuarios_unicos = analytics_db.get_unique_users(days=30)
```

---

#### 4. get_visits_by_user()
```python
def get_visits_by_user(self, days=30, limit=20)
```
**Descripción**: Obtiene estadísticas de visitas por usuario, ordenadas por frecuencia.

**Parámetros**:
- `days` (int): Número de días hacia atrás (default: 30)
- `limit` (int): Número máximo de resultados (default: 20)

**Retorna**: `list[dict]` - Lista de diccionarios con:
- `user_email`: Email del usuario
- `user_name`: Nombre del usuario
- `visit_count`: Número de visitas
- `last_visit`: Fecha y hora de última visita

**Ejemplo**:
```python
usuarios_activos = analytics_db.get_visits_by_user(days=7, limit=10)
for usuario in usuarios_activos:
    print(f"{usuario['user_name']}: {usuario['visit_count']} visitas")
```

---

#### 5. get_visits_by_page()
```python
def get_visits_by_page(self, days=30)
```
**Descripción**: Obtiene estadísticas de visitas agrupadas por página.

**Parámetros**:
- `days` (int): Número de días hacia atrás (default: 30)

**Retorna**: `list[dict]` - Lista de diccionarios con:
- `page_url`: URL de la página
- `page_title`: Título de la página
- `visit_count`: Número de visitas

**Ejemplo**:
```python
paginas = analytics_db.get_visits_by_page(days=30)
for pagina in paginas:
    print(f"{pagina['page_title']}: {pagina['visit_count']} visitas")
```

---

#### 6. get_visits_by_day()
```python
def get_visits_by_day(self, days=30)
```
**Descripción**: Obtiene visitas agrupadas por día.

**Parámetros**:
- `days` (int): Número de días hacia atrás (default: 30)

**Retorna**: `list[dict]` - Lista de diccionarios con:
- `visit_date`: Fecha
- `visit_count`: Número de visitas en ese día
- `unique_users`: Usuarios únicos en ese día

**Ejemplo**:
```python
visitas_diarias = analytics_db.get_visits_by_day(days=7)
for dia in visitas_diarias:
    print(f"{dia['visit_date']}: {dia['visit_count']} visitas")
```

---

#### 7. get_visits_by_hour()
```python
def get_visits_by_hour(self, days=7)
```
**Descripción**: Obtiene visitas agrupadas por hora del día.

**Parámetros**:
- `days` (int): Número de días hacia atrás (default: 7)

**Retorna**: `list[dict]` - Lista de diccionarios con:
- `hour`: Hora del día (0-23)
- `visit_count`: Número de visitas en esa hora

**Ejemplo**:
```python
horas_pico = analytics_db.get_visits_by_hour(days=7)
for hora in horas_pico:
    print(f"{hora['hour']}:00 - {hora['visit_count']} visitas")
```

---

#### 8. get_recent_visits()
```python
def get_recent_visits(self, limit=50)
```
**Descripción**: Obtiene las visitas más recientes del sistema.

**Parámetros**:
- `limit` (int): Número máximo de visitas a retornar (default: 50)

**Retorna**: `list[dict]` - Lista de diccionarios con:
- `user_email`: Email del usuario
- `user_name`: Nombre del usuario
- `page_url`: URL visitada
- `page_title`: Título de la página
- `visit_timestamp`: Fecha y hora de la visita
- `ip_address`: Dirección IP

**Ejemplo**:
```python
ultimas_visitas = analytics_db.get_recent_visits(limit=20)
for visita in ultimas_visitas:
    print(f"{visita['user_name']} visitó {visita['page_title']} a las {visita['visit_timestamp']}")
```

---

## 🌐 Endpoint de Flask

### Ruta: `/analytics`
```python
@app.route('/analytics')
def analytics()
```

**Descripción**: Endpoint que renderiza el dashboard de analytics.

**Características**:
- Requiere autenticación de usuario
- Restringido a usuarios administradores
- Soporta filtrado por período de tiempo

**Parámetros URL**:
- `period` (int, opcional): Número de días a analizar (default: 30)
  - Ejemplo: `/analytics?period=7`

**Respuesta**: Renderiza `analytics.html` con datos estadísticos

**Datos enviados al template**:
```python
stats = {
    'total_visits': int,                    # Total de visitas
    'unique_users': int,                    # Usuarios únicos
    'total_allowed_users': int,             # Total de usuarios permitidos
    'visits_by_user': list[dict],           # Visitas por usuario
    'visits_by_page': list[dict],           # Visitas por página
    'visits_by_day': list[dict],            # Visitas por día
    'visits_by_hour': list[dict],           # Visitas por hora
    'recent_visits': list[dict]             # Visitas recientes
}
```

**Control de Acceso**:
```python
admin_emails = [
    'jonathan.cerda@agrovetmarket.com',
    'juan.portal@agrovetmarket.com',
    'ena.fernandez@agrovetmarket.com',
    'juana.lobaton@agrovetmarket.com'
]
```

---

## 🎨 Interfaz de Usuario (analytics.html)

### Componentes Visuales

#### 1. Tarjetas de Estadísticas (Stats Cards)
- **Total de Visitas**: Muestra el número total de visitas
- **Usuarios Únicos**: Muestra usuarios únicos y porcentaje de usuarios activos
- **Promedio Visitas/Usuario**: Calcula el promedio de visitas por usuario
- **Páginas Únicas**: Número de páginas diferentes visitadas

#### 2. Selector de Período
```html
<select onchange="changePeriod(this.value)">
    <option value="7">Últimos 7 días</option>
    <option value="30">Últimos 30 días</option>
    <option value="90">Últimos 90 días</option>
</select>
```

#### 3. Gráficos (Google Charts)

**a) Gráfico de Líneas - Visitas por Día**
- Muestra tendencia de visitas diarias
- Incluye línea de usuarios únicos
- Colores: `#875A7B` (visitas), `#00A09D` (usuarios únicos)

**b) Gráfico de Columnas - Visitas por Hora**
- Muestra distribución de visitas por hora del día (0-23)
- Identifica horas pico de uso
- Color: `#875A7B`

#### 4. Tablas de Datos

**a) Usuarios Más Activos**
| Columna | Descripción |
|---------|-------------|
| # | Posición |
| Usuario | Nombre del usuario |
| Email | Correo electrónico |
| Visitas | Número de visitas (badge) |
| Última Visita | Fecha y hora formateada |

**b) Páginas Más Visitadas**
| Columna | Descripción |
|---------|-------------|
| # | Posición |
| Página | Título de la página |
| URL | Ruta de la página (código) |
| Visitas | Número de visitas (badge) |
| % del Total | Porcentaje del total de visitas |

**c) Visitas Recientes**
| Columna | Descripción |
|---------|-------------|
| Fecha y Hora | Timestamp de la visita |
| Usuario | Nombre del usuario |
| Página | Título o URL de la página |
| IP | Dirección IP del visitante |

---

## 🗄️ Modelo de Base de Datos

### Tabla: `page_visits`

```sql
CREATE TABLE page_visits (
    id                  SERIAL PRIMARY KEY,
    user_email          VARCHAR(255) NOT NULL,
    user_name           VARCHAR(255),
    page_url            VARCHAR(500) NOT NULL,
    page_title          VARCHAR(255),
    visit_timestamp     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    session_duration    INTEGER DEFAULT 0,
    ip_address          VARCHAR(50),
    user_agent          TEXT,
    referrer            VARCHAR(500),
    method              VARCHAR(10)
);
```

### Índices
```sql
-- Índice para búsquedas por usuario
CREATE INDEX idx_visits_user ON page_visits(user_email);

-- Índice para búsquedas por fecha (descendente)
CREATE INDEX idx_visits_timestamp ON page_visits(visit_timestamp DESC);

-- Índice para búsquedas por página
CREATE INDEX idx_visits_page ON page_visits(page_url);
```

---

## 🚀 Implementación en Nuevo Proyecto

### Paso 1: Instalación de Dependencias
```bash
pip install flask psycopg2-binary pytz
```

### Paso 2: Configuración de Variables de Entorno
```bash
# Para producción (PostgreSQL)
export DATABASE_URL="postgresql://user:password@host:port/database"

# Para desarrollo (SQLite - automático)
# No requiere configuración
```

### Paso 3: Inicialización en Flask
```python
from analytics_db import AnalyticsDB

# Crear instancia global
analytics_db = AnalyticsDB()

# Registrar visitas en decorador o middleware
@app.before_request
def log_page_visit():
    if 'username' in session:
        analytics_db.log_visit(
            user_email=session.get('username'),
            user_name=session.get('user_name'),
            page_url=request.path,
            page_title=request.endpoint,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            referrer=request.referrer,
            method=request.method
        )
```

### Paso 4: Crear Ruta de Analytics
```python
@app.route('/analytics')
def analytics():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Verificar permisos de administrador
    if not is_admin(session.get('username')):
        flash('No tienes permisos para acceder a esta sección.', 'danger')
        return redirect(url_for('index'))
    
    # Obtener período
    days = request.args.get('period', 30, type=int)
    
    # Recopilar estadísticas
    stats = {
        'total_visits': analytics_db.get_total_visits(days),
        'unique_users': analytics_db.get_unique_users(days),
        'visits_by_user': [dict(row) for row in analytics_db.get_visits_by_user(days)],
        'visits_by_page': [dict(row) for row in analytics_db.get_visits_by_page(days)],
        'visits_by_day': [dict(row) for row in analytics_db.get_visits_by_day(days)],
        'visits_by_hour': [dict(row) for row in analytics_db.get_visits_by_hour(min(days, 7))],
        'recent_visits': [dict(row) for row in analytics_db.get_recent_visits(50)]
    }
    
    return render_template('analytics.html', stats=stats, period=days)
```

---

## 📊 Métricas y KPIs Disponibles

### Métricas Básicas
- Total de visitas
- Usuarios únicos
- Páginas únicas visitadas
- Promedio de visitas por usuario

### Análisis Temporal
- Visitas por día (tendencias)
- Visitas por hora (patrones de uso)
- Identificación de horas pico

### Análisis de Usuarios
- Usuarios más activos
- Última actividad de cada usuario
- Tasa de usuarios activos vs. total

### Análisis de Páginas
- Páginas más visitadas
- Porcentaje de visitas por página
- Popularidad de contenido

### Monitoreo en Tiempo Real
- Visitas recientes (últimas 50)
- Actividad actual del sistema

---

## 🔒 Características de Seguridad

### Control de Acceso
- Autenticación requerida para acceder
- Lista blanca de administradores
- Redirección automática si no hay permisos

### Privacidad de Datos
- Exclusión automática de usuarios administradores en estadísticas
- Almacenamiento seguro de IPs
- Gestión de timezones para correcta atribución temporal

### Manejo de Errores
- Try-catch en todas las operaciones de BD
- Logging de errores con emojis descriptivos
- Fallback automático a SQLite si PostgreSQL falla

---

## 🎯 Casos de Uso

### 1. Monitoreo de Adopción
Medir cuántos usuarios están usando activamente el sistema.
```python
usuarios_activos = analytics_db.get_unique_users(days=30)
tasa_adopcion = (usuarios_activos / total_usuarios) * 100
```

### 2. Identificación de Funcionalidades Populares
Determinar qué páginas son más visitadas.
```python
paginas_populares = analytics_db.get_visits_by_page(days=7)
top_3 = paginas_populares[:3]
```

### 3. Análisis de Patrones de Uso
Identificar horas pico para planificar mantenimiento.
```python
horas = analytics_db.get_visits_by_hour(days=7)
hora_menor_uso = min(horas, key=lambda x: x['visit_count'])
```

### 4. Detección de Usuarios Inactivos
Identificar usuarios que no han ingresado recientemente.
```python
usuarios_recientes = analytics_db.get_visits_by_user(days=7)
emails_activos = [u['user_email'] for u in usuarios_recientes]
# Comparar con lista total de usuarios
```

---

## 📈 Extensiones Futuras

### Funcionalidades Sugeridas
1. **Duración de Sesión**: Calcular tiempo promedio en cada página
2. **Dashboards Personalizados**: Filtros por usuario, departamento, rol
3. **Alertas**: Notificaciones cuando métricas superen umbrales
4. **Exportación**: Descargar reportes en PDF/Excel
5. **Comparación de Períodos**: Comparar semana actual vs. anterior
6. **Funnel de Conversión**: Seguimiento de secuencias de páginas
7. **Mapas de Calor**: Visualización de clics y áreas de interés
8. **A/B Testing**: Comparación de variantes de UI

### Mejoras de Rendimiento
- Implementar caché Redis para consultas frecuentes
- Agregaciones pre-calculadas para períodos largos
- Particionamiento de tablas por fecha
- Índices adicionales según patrones de consulta

---

## 📝 Notas de Implementación

### Timezone
- Sistema configurado para **America/Lima (UTC-5)**
- Todos los timestamps se convierten automáticamente
- Compatible con horarios de verano

### Compatibilidad
- **SQLite**: Para desarrollo local
- **PostgreSQL**: Para producción
- Detección automática según `DATABASE_URL`

### Rendimiento
- Índices optimizados para consultas frecuentes
- Context managers para gestión correcta de conexiones
- Rollback automático en caso de error

### Exclusiones
- Usuario `jonathan.cerda@agrovetmarket.com` excluido de estadísticas
- Configurable para excluir otros usuarios de prueba

---

## 🛠️ Troubleshooting

### Problema: "psycopg2 no disponible"
```bash
pip install psycopg2-binary
```

### Problema: Timezone incorrecto
Verificar configuración:
```python
import pytz
PERU_TZ = pytz.timezone('America/Lima')
```

### Problema: Tablas no se crean
Verificar permisos de base de datos y ejecutar:
```python
analytics_db = AnalyticsDB()
# Las tablas se crean automáticamente en __init__
```

---

## 📞 Soporte

Para soporte técnico o preguntas sobre implementación, contactar al equipo de desarrollo.

**Autor**: Sistema desarrollado para Dashboard de Ventas Agrovet Market  
**Versión**: 1.0  
**Última Actualización**: 2025

---

## 📄 Licencia

Sistema interno de uso exclusivo del proyecto.
