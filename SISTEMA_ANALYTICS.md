# 📊 Sistema de Analytics - Inventario Stock

## Descripción General

Sistema completo de monitoreo y análisis de visitas implementado en el proyecto de Inventario Stock. Permite rastrear el uso del sistema, analizar patrones de comportamiento de usuarios y generar reportes estadísticos detallados.

---

## 🎯 Características Implementadas

### ✅ Tracking Automático de Visitas
- Registro automático de todas las visitas a páginas del sistema
- Captura de: usuario, página, timestamp, IP, user-agent, referrer
- Zona horaria: Detecta automáticamente la zona horaria local del sistema
- **Exclusiones**: No se registran visitas de jonathan.cerda@agrovetmarket.com (administrador)

### ✅ Dashboard de Analytics
- Acceso exclusivo para administradores
- Visualizaciones interactivas con Google Charts
- Filtrado por período (7, 30, 90 días)

### ✅ Métricas Disponibles

#### KPIs Principales
- **Total de Visitas**: Número total de visitas en el período
- **Usuarios Únicos**: Usuarios diferentes que han accedido
- **Promedio Visitas/Usuario**: Engagement promedio
- **Páginas Únicas**: Número de páginas diferentes visitadas
- **Tasa de Adopción**: % de usuarios activos vs. total autorizados

#### Análisis Temporal
- **Visitas por Día**: Gráfico de líneas con tendencia
- **Visitas por Hora**: Identificación de horas pico de uso

#### Análisis de Usuarios
- **Usuarios Más Activos**: Top usuarios por número de visitas
- **Última Actividad**: Fecha y hora de última visita

#### Análisis de Páginas
- **Páginas Más Visitadas**: Ranking de páginas por popularidad
- **Porcentaje del Total**: Distribución de visitas por página

#### Monitoreo en Tiempo Real
- **Visitas Recientes**: Últimas 50 visitas al sistema

---

## 🔐 Control de Acceso

### Usuarios Administradores
Solo estos usuarios pueden acceder a `/analytics`:
- jonathan.cerda@agrovetmarket.com
- ena.fernandez@agrovetmarket.com

### Exclusión de Tracking
**Importante**: Las visitas de jonathan.cerda@agrovetmarket.com NO se registran en analytics para evitar sesgar las estadísticas.

### Botón de Acceso
Los administradores verán un botón **📊 Analytics** en:
- Dashboard principal
- Página de inventario

---

## 🗄️ Base de Datos

### Desarrollo (SQLite)
- Base de datos automática: `analytics.db`
- Sin configuración adicional necesaria
- Ideal para testing y desarrollo local

### Producción (PostgreSQL)
- Configurar variable de entorno: `DATABASE_URL`
- Formato: `postgresql://user:password@host:port/database`
- Migración automática al detectar PostgreSQL

### Tabla: `page_visits`
```sql
- id (PRIMARY KEY)
- user_email (VARCHAR/TEXT)
- user_name (VARCHAR/TEXT)
- page_url (VARCHAR/TEXT)
- page_title (VARCHAR/TEXT)
- visit_timestamp (TIMESTAMP)
- session_duration (INTEGER)
- ip_address (VARCHAR/TEXT)
- user_agent (TEXT)
- referrer (VARCHAR/TEXT)
- method (VARCHAR/TEXT)
```

### Índices Optimizados
- `idx_visits_user`: Por email de usuario
- `idx_visits_timestamp`: Por fecha (descendente)
- `idx_visits_page`: Por URL de página

---

## 🚀 Cómo Usar

### 1. Instalación de Dependencias
```bash
pip install -r requirements.txt
```

Dependencias nuevas agregadas:
- `pytz` (ya estaba)
- `psycopg2-binary` (nuevo - para PostgreSQL en producción)

### 2. Iniciar el Sistema
```bash
python app.py
```

El sistema iniciará automáticamente:
```
📊 Analytics usando SQLite (desarrollo)
📊 Tablas de analytics creadas correctamente
```

### 3. Acceder al Dashboard
1. Inicia sesión con una cuenta de administrador
2. Haz clic en el botón **📊 Analytics**
3. Selecciona el período deseado (7, 30 o 90 días)

---

## 📈 Interpretación de Métricas

### Tasa de Adopción
```
Fórmula: (Usuarios Únicos / Total Usuarios Autorizados) × 100
Objetivo: > 70% en 30 días
```

### Promedio Visitas/Usuario
```
Fórmula: Total de Visitas / Usuarios Únicos
Interpretación:
  < 5: Uso ocasional
  5-15: Uso regular
  > 15: Uso intensivo
```

### Horas Pico
Identifica cuándo hay más actividad para:
- Planificar mantenimientos en horas de menor uso
- Optimizar recursos del servidor
- Programar actualizaciones

### Páginas Populares
- Alta visita a Dashboard: Usuarios consultan métricas
- Alta visita a Inventario: Usuarios trabajan con datos
- Baja visita a páginas: Posible necesidad de rediseño

---

## 🔧 Configuración Avanzada

### Excluir Páginas del Tracking
Editar en `app.py`:
```python
excluded_endpoints = ['static', 'export_excel', 'export_excel_exportacion', 'tu_endpoint']
```

### Cambiar Lista de Administradores
Editar en `app.py` (ruta `/analytics`):
```python
admin_emails = [
    'nuevo_admin@empresa.com',
    'otro_admin@empresa.com'
]
```

### Configurar PostgreSQL en Producción
```bash
export DATABASE_URL="postgresql://username:password@hostname:5432/database_name"
```

---

## 📊 Visualizaciones Disponibles

### 1. Gráfico de Líneas - Visitas por Día
- Línea morada: Total de visitas
- Línea verde: Usuarios únicos
- Identifica tendencias y patrones semanales

### 2. Gráfico de Columnas - Visitas por Hora
- Rango: 0:00 a 23:00
- Color morado corporativo
- Identifica horas pico y valles

### 3. Tablas Interactivas
- Hover effects para mejor UX
- Badges de color para métricas destacadas
- Ordenamiento por relevancia

---

## 🛠️ Troubleshooting

### Error: "analytics.db is locked"
**Solución**: Cerrar otras conexiones o reiniciar el servidor

### No se registran visitas
**Verificar**:
1. Usuario tiene sesión activa
2. Endpoint no está en lista de exclusión
3. Base de datos tiene permisos de escritura

### Gráficos no se cargan
**Solución**: 
1. Verificar conexión a internet (Google Charts CDN)
2. Revisar consola del navegador para errores JS
3. Verificar que hay datos en el período seleccionado

### Error de timezone
**Verificar** que pytz está instalado:
```bash
pip install pytz
```

---

## 📝 Archivos Modificados/Creados

### Archivos Nuevos
- `analytics_db.py`: Clase de gestión de base de datos
- `templates/analytics.html`: Dashboard de visualización
- `SISTEMA_ANALYTICS.md`: Esta documentación

### Archivos Modificados
- `app.py`: 
  - Importación de AnalyticsDB
  - Middleware @app.before_request
  - Ruta /analytics
- `templates/dashboard.html`: Botón de Analytics para admins
- `templates/inventory.html`: Botón de Analytics para admins
- `requirements.txt`: Agregado psycopg2-binary

---

## 🎓 Casos de Uso

### 1. Monitoreo de Adopción del Sistema
Ver cuántos usuarios están usando activamente el sistema después del lanzamiento.

### 2. Identificar Funcionalidades Populares
Determinar qué módulos necesitan más atención o mejoras.

### 3. Optimización de Recursos
Identificar horas de menor uso para mantenimiento programado.

### 4. Detección de Problemas
Si una página tiene cero visitas, puede indicar problemas de acceso o diseño.

### 5. Reportes para Stakeholders
Demostrar el ROI y nivel de uso del sistema.

---

## 🔮 Extensiones Futuras Sugeridas

### Mejoras de Funcionalidad
- [ ] Duración de sesión por página
- [ ] Funnel de conversión entre páginas
- [ ] Exportación de reportes a PDF/Excel
- [ ] Alertas automáticas por email
- [ ] Comparación de períodos (semana actual vs. anterior)
- [ ] Segmentación por departamento/equipo
- [ ] Dashboards personalizables por usuario

### Mejoras de Rendimiento
- [ ] Cache Redis para consultas frecuentes
- [ ] Agregaciones pre-calculadas
- [ ] Particionamiento de tablas por fecha
- [ ] API REST para integraciones externas

### Mejoras de UX
- [ ] Modo oscuro
- [ ] Exportación de gráficos como imagen
- [ ] Filtros avanzados interactivos
- [ ] Comparación side-by-side de métricas

---

## 📞 Soporte Técnico

Para preguntas o problemas con el sistema de analytics, contactar a:
- Jonathan Cerda (jonathan.cerda@agrovetmarket.com)
- Equipo de Desarrollo

---

## 📄 Licencia

Sistema interno de uso exclusivo para Inventario Stock - Agrovet Market.

**Versión**: 1.0  
**Fecha de Implementación**: 23 de febrero de 2026  
**Última Actualización**: 23 de febrero de 2026
