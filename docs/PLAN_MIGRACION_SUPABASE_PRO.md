# Plan de Migración: Supabase Free → Supabase Pro

**Versión:** 1.0  
**Fecha:** 1 de abril de 2026  
**Responsable:** Jonathan Cerda  
**Proyecto:** Inventario Stock Web  
**Estado:** 📋 PLANIFICACIÓN

---

## 📊 Resumen Ejecutivo

### Objetivo
Migrar la base de datos de analytics desde el proyecto actual de Supabase Free tier al nuevo proyecto Supabase Pro, aprovechando las mejoras de rendimiento, almacenamiento y funcionalidades avanzadas.

### Proyecto Actual (Origen)
- **Tier:** Free
- **Project Ref:** `ppmbwujtfueilifisxhs`
- **Región:** US West 1 (AWS)
- **URL Actual:** `postgresql://postgres.ppmbwujtfueilifisxhs:[PASSWORD]@aws-0-us-west-1.pooler.supabase.com:6543/postgres`

### Proyecto Nuevo (Destino)
- **Tier:** Pro
- **Project Ref:** ⚠️ Por crear
- **Región:** ⚠️ Por definir (recomendado: misma región o más cercana a Render)
- **URL Nueva:** ⚠️ Se generará después de crear el proyecto

---

## 🗄️ Inventario de Base de Datos Actual

### Tabla 1: `page_visits` (Analytics de Usuarios)

**Propósito:** Registro de visitas de usuarios al sistema

| Columna | Tipo | Constraints | Descripción |
|---------|------|-------------|-------------|
| `id` | SERIAL | PRIMARY KEY | ID autoincremental |
| `user_email` | VARCHAR(255) | NOT NULL | Email del usuario (de Google OAuth) |
| `user_name` | VARCHAR(255) | - | Nombre completo del usuario |
| `page_url` | VARCHAR(500) | NOT NULL | URL de la página visitada |
| `page_title` | VARCHAR(255) | - | Título de la página (endpoint de Flask) |
| `visit_timestamp` | TIMESTAMP | NOT NULL | Fecha/hora de la visita (America/Lima) |
| `session_duration` | INTEGER | DEFAULT 0 | Duración de la sesión en segundos |
| `ip_address` | VARCHAR(50) | - | IP del cliente |
| `user_agent` | TEXT | - | User agent del navegador |
| `referrer` | VARCHAR(500) | - | URL de referencia |
| `method` | VARCHAR(10) | - | Método HTTP (GET/POST) |

### Índices Activos
```sql
-- Índice para búsquedas por usuario
CREATE INDEX idx_visits_user ON page_visits(user_email);

-- Índice para consultas por fecha (DESC para últimas visitas)
CREATE INDEX idx_visits_timestamp ON page_visits(visit_timestamp DESC);

-- Índice para análisis por página
CREATE INDEX idx_visits_page ON page_visits(page_url);
```

### Estimación de Datos
- **Filas estimadas:** ⚠️ Por determinar (ejecutar count antes de migrar)
- **Tamaño estimado:** ⚠️ Por calcular
- **Período de datos:** Desde implementación de analytics (~marzo 2026)

---

## 📋 Plan de Migración - 7 Fases

### **FASE 1: Preparación y Análisis** 🔍
**Duración estimada:** 1 hora  
**Estado:** ⬜ Pendiente

#### 1.1 Análisis de Datos Actual
- [ ] Conectarse a Supabase Free actual
- [ ] Ejecutar `SELECT COUNT(*) FROM page_visits;`
- [ ] Ejecutar `SELECT pg_size_pretty(pg_total_relation_size('page_visits'));`
- [ ] Exportar schema actual: `pg_dump -s -t page_visits`
- [ ] Identificar datos críticos vs datos prescindibles

#### 1.2 Backup de Seguridad
```bash
# Backup completo de la tabla
pg_dump -h aws-0-us-west-1.pooler.supabase.com \
        -U postgres.ppmbwujtfueilifisxhs \
        -p 6543 \
        -d postgres \
        -t page_visits \
        --no-owner --no-acl \
        -f backup_page_visits_$(date +%Y%m%d).sql
```

- [ ] Crear backup SQL de estructura + datos
- [ ] Guardar backup en carpeta local `backups/`
- [ ] Verificar integridad del backup (restaurar en SQLite de prueba)
- [ ] Subir backup a Google Drive o similar (redundancia)

#### 1.3 Documentación de Estado Actual
- [ ] Documentar número total de filas
- [ ] Documentar tamaño de la base de datos
- [ ] Listar todas las dependencias (API keys, conexiones)
- [ ] Capturar screenshots del panel de Supabase actual

---

### **FASE 2: Creación del Nuevo Proyecto Pro** 🆕
**Duración estimada:** 30 minutos  
**Estado:** ⬜ Pendiente

#### 2.1 Crear Proyecto en Supabase
- [ ] Ir a [supabase.com/dashboard](https://supabase.com/dashboard)
- [ ] Click en "New Project"
- [ ] **Configuración del Proyecto:**
  - **Name:** `inventario-stock-pro` (o nombre descriptivo)
  - **Database Password:** Generar password seguro (guardar en 1Password/Bitwarden)
  - **Region:** Seleccionar región óptima (recomendado: `us-east-1` si Render está ahí)
  - **Pricing Plan:** Pro ($25/mes)
- [ ] Esperar a que el proyecto se provisione (~2 minutos)
- [ ] Guardar el nuevo **Project Ref** (formato: `xyz123abc456`)

#### 2.2 Obtener Credenciales de Conexión
- [ ] Ir a Settings → Database
- [ ] Copiar **Connection String (Session mode):**
  ```
  postgresql://postgres.[PROJECT_REF]:[YOUR_PASSWORD]@aws-0-[REGION].pooler.supabase.com:5432/postgres
  ```
- [ ] Copiar **Connection Pooler (Transaction mode):**
  ```
  postgresql://postgres.[PROJECT_REF]:[YOUR_PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
  ```
- [ ] Guardar ambas URLs en archivo `.env.new` (temporal)

#### 2.3 Configuración Inicial del Proyecto Pro
- [ ] Habilitar extensiones necesarias (si aplica):
  - `pg_stat_statements` (monitoreo de queries)
  - `uuid-ossp` (si se usará en el futuro)
- [ ] Configurar timezone: `SET timezone = 'America/Lima';`
- [ ] Revisar límites del plan Pro en Settings → Billing

---

### **FASE 3: Recreación de Estructura** 🏗️
**Duración estimada:** 30 minutos  
**Estado:** ⬜ Pendiente

#### 3.1 Crear Tabla en Proyecto Pro
Usar el script mejorado:

```sql
-- ============================================
-- SCRIPT DE MIGRACIÓN - SUPABASE PRO
-- ============================================
-- Proyecto: Inventario Stock Web
-- Fecha: 2026-04-01
-- Tier: Pro
-- ============================================

-- Crear tabla de visitas (estructura mejorada)
CREATE TABLE IF NOT EXISTS page_visits (
    id SERIAL PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL,
    user_name VARCHAR(255),
    page_url VARCHAR(500) NOT NULL,
    page_title VARCHAR(255),
    visit_timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    session_duration INTEGER DEFAULT 0,
    ip_address VARCHAR(50),
    user_agent TEXT,
    referrer VARCHAR(500),
    method VARCHAR(10) DEFAULT 'GET',
    
    -- Mejoras para Pro
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices optimizados
CREATE INDEX IF NOT EXISTS idx_visits_user ON page_visits(user_email);
CREATE INDEX IF NOT EXISTS idx_visits_timestamp ON page_visits(visit_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_visits_page ON page_visits(page_url);
CREATE INDEX IF NOT EXISTS idx_visits_created_at ON page_visits(created_at DESC);

-- Índices compuestos para queries complejas
CREATE INDEX IF NOT EXISTS idx_visits_user_timestamp ON page_visits(user_email, visit_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_visits_page_timestamp ON page_visits(page_url, visit_timestamp DESC);

-- Comentarios para documentación
COMMENT ON TABLE page_visits IS 'Registro de visitas de usuarios al sistema inventario-stock (Supabase Pro)';
COMMENT ON COLUMN page_visits.visit_timestamp IS 'Timestamp con timezone America/Lima';
COMMENT ON COLUMN page_visits.session_duration IS 'Duración de sesión en segundos (experimental)';

-- Función para auto-actualizar updated_at (mejora Pro)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para updated_at
CREATE TRIGGER update_page_visits_updated_at
    BEFORE UPDATE ON page_visits
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Verificar creación
SELECT 
    'Tabla creada exitosamente en Supabase Pro' as status,
    COUNT(*) as total_columns
FROM information_schema.columns 
WHERE table_name = 'page_visits';

-- Verificar índices
SELECT 
    indexname as indice,
    indexdef as definicion
FROM pg_indexes 
WHERE tablename = 'page_visits'
ORDER BY indexname;
```

- [ ] Ejecutar script en SQL Editor de Supabase Pro
- [ ] Verificar que la tabla se creó correctamente
- [ ] Verificar que todos los índices están activos
- [ ] Probar inserción de prueba:
  ```sql
  INSERT INTO page_visits (user_email, user_name, page_url, page_title)
  VALUES ('test@example.com', 'Test User', '/dashboard', 'dashboard');
  ```
- [ ] Eliminar fila de prueba: `DELETE FROM page_visits WHERE user_email = 'test@example.com';`

---

### **FASE 4: Migración de Datos** 📦
**Duración estimada:** 1-2 horas (depende del volumen)  
**Estado:** ⬜ Pendiente

#### 4.1 Opción A: Migración Directa (Recomendado si <10k filas)

**Usando pg_dump y psql:**
```bash
# 1. Exportar solo los datos (sin estructura)
pg_dump -h aws-0-us-west-1.pooler.supabase.com \
        -U postgres.ppmbwujtfueilifisxhs \
        -p 6543 \
        -d postgres \
        -t page_visits \
        --data-only \
        --no-owner --no-acl \
        -f data_page_visits_$(date +%Y%m%d).sql

# 2. Importar al nuevo proyecto Pro
psql -h aws-0-[NEW_REGION].pooler.supabase.com \
     -U postgres.[NEW_PROJECT_REF] \
     -p 5432 \
     -d postgres \
     -f data_page_visits_$(date +%Y%m%d).sql
```

- [ ] Ejecutar export de datos
- [ ] Revisar el archivo SQL generado (buscar errores)
- [ ] Ejecutar import en proyecto Pro
- [ ] Verificar count en destino: `SELECT COUNT(*) FROM page_visits;`
- [ ] Comparar con count en origen

#### 4.2 Opción B: Migración por CSV (Alternativa si falla A)

```bash
# 1. Exportar a CSV
psql -h aws-0-us-west-1.pooler.supabase.com \
     -U postgres.ppmbwujtfueilifisxhs \
     -p 6543 \
     -d postgres \
     -c "\COPY page_visits TO 'page_visits_export.csv' WITH CSV HEADER"

# 2. Importar desde CSV
psql -h aws-0-[NEW_REGION].pooler.supabase.com \
     -U postgres.[NEW_PROJECT_REF] \
     -p 5432 \
     -d postgres \
     -c "\COPY page_visits FROM 'page_visits_export.csv' WITH CSV HEADER"
```

- [ ] Ejecutar export a CSV
- [ ] Validar formato del CSV
- [ ] Ejecutar import desde CSV
- [ ] Verificar integridad de datos

#### 4.3 Opción C: Migración Programática (Si >10k filas)

Crear script Python temporal:
```python
# migrate_data.py
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

# Conexiones
OLD_DB = "postgresql://postgres.ppmbwujtfueilifisxhs:PASSWORD@aws-0-us-west-1.pooler.supabase.com:6543/postgres"
NEW_DB = "postgresql://postgres.NEW_REF:PASSWORD@aws-0-NEW_REGION.pooler.supabase.com:5432/postgres"

def migrate_data():
    # Conectar a ambas DB
    old_conn = psycopg2.connect(OLD_DB)
    new_conn = psycopg2.connect(NEW_DB)
    
    old_cursor = old_conn.cursor()
    new_cursor = new_conn.cursor()
    
    # Exportar datos
    print("Leyendo datos del proyecto antiguo...")
    old_cursor.execute("SELECT * FROM page_visits ORDER BY id")
    rows = old_cursor.fetchall()
    print(f"Total de filas a migrar: {len(rows)}")
    
    # Importar en lotes
    batch_size = 1000
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i+batch_size]
        for row in batch:
            new_cursor.execute("""
                INSERT INTO page_visits 
                (id, user_email, user_name, page_url, page_title, visit_timestamp, 
                 session_duration, ip_address, user_agent, referrer, method)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, row)
        new_conn.commit()
        print(f"Migradas {min(i+batch_size, len(rows))} / {len(rows)} filas")
    
    # Actualizar secuencia
    new_cursor.execute("SELECT setval('page_visits_id_seq', (SELECT MAX(id) FROM page_visits));")
    new_conn.commit()
    
    print("✅ Migración completada!")
    
    old_conn.close()
    new_conn.close()

if __name__ == "__main__":
    migrate_data()
```

- [ ] Crear `migrate_data.py` con las credenciales correctas
- [ ] Ejecutar: `python migrate_data.py`
- [ ] Monitorear progreso
- [ ] Verificar que la secuencia id esté correcta

#### 4.4 Validación Post-Migración
```sql
-- Comparar counts
SELECT COUNT(*) FROM page_visits; -- Ejecutar en ambas DB

-- Verificar rango de fechas
SELECT MIN(visit_timestamp), MAX(visit_timestamp) FROM page_visits;

-- Verificar usuarios únicos
SELECT COUNT(DISTINCT user_email) FROM page_visits;

-- Verificar integridad de índices
REINDEX TABLE page_visits;

-- Ejecutar ANALYZE para estadísticas
ANALYZE page_visits;
```

- [ ] Ejecutar queries de validación
- [ ] Comparar resultados origen vs destino
- [ ] Documentar cualquier discrepancia

---

### **FASE 5: Actualización de Código** 💻
**Duración estimada:** 30 minutos  
**Estado:** ⬜ Pendiente

#### 5.1 Actualizar Variables de Entorno

**Archivo `.env` (local):**
```env
# ===== ANALYTICS SUPABASE PRO =====
DATABASE_URL=postgresql://postgres.[NEW_PROJECT_REF]:[PASSWORD]@aws-0-[NEW_REGION].pooler.supabase.com:6543/postgres

# Opcional: prefijo de tablas (dejar vacío si no es necesario)
ANALYTICS_TABLE_PREFIX=
```

**En Render (producción):**
- [ ] Ir a Dashboard → inventario-stock-web → Environment
- [ ] **NO BORRAR** `DATABASE_URL` antiguo todavía (backup)
- [ ] Agregar nueva variable temporal: `DATABASE_URL_NEW=postgresql://...`
- [ ] Cambiar código temporalmente para usar `DATABASE_URL_NEW`
- [ ] Después de probar, renombrar `DATABASE_URL_NEW` → `DATABASE_URL`

#### 5.2 Actualizar Documentación

**Archivos a actualizar:**
- [ ] `README.md` - Actualizar Project Ref y región
- [ ] `.env.example` - Actualizar URL de ejemplo
- [ ] `create_analytics_table.sql` - Actualizar comentarios
- [ ] Crear este documento: `docs/PLAN_MIGRACION_SUPABASE_PRO.md`

#### 5.3 Probar Conexión Local
```bash
# Activar entorno virtual
.\venv\Scripts\Activate.ps1

# Probar conexión
python -c "from analytics_db import AnalyticsDB; db = AnalyticsDB(); print('✅ Conexión exitosa')"

# Probar lectura
python -c "from analytics_db import AnalyticsDB; db = AnalyticsDB(); print(f'Total visitas: {db.get_total_visits()}')"
```

- [ ] Ejecutar pruebas de conexión
- [ ] Verificar que lee datos correctamente
- [ ] Probar inserción de prueba (log_visit)

---

### **FASE 6: Testing y Validación** 🧪
**Duración estimada:** 1 hora  
**Estado:** ⬜ Pendiente

#### 6.1 Testing Local
```bash
# Ejecutar suite de tests
pytest tests/test_analytics_db.py -v

# Probar endpoints de analytics (si app está corriendo)
python app.py
# Navegar a http://localhost:5000/analytics
```

- [ ] Todos los tests pasan
- [ ] Dashboard de analytics carga correctamente
- [ ] Gráficos muestran datos históricos
- [ ] Exportaciones funcionan

#### 6.2 Testing en Staging (si aplica)
Si tienes un ambiente de staging en Render:
- [ ] Actualizar `DATABASE_URL` en staging
- [ ] Redeploy staging
- [ ] Probar funcionalidad completa
- [ ] Verificar logs de errores

#### 6.3 Benchmarking (aprovechar Pro)
```sql
-- Ejecutar query pesada para medir rendimiento
EXPLAIN ANALYZE
SELECT user_email, COUNT(*) as visits
FROM page_visits
WHERE visit_timestamp > NOW() - INTERVAL '30 days'
GROUP BY user_email
ORDER BY visits DESC;
```

- [ ] Comparar tiempos de ejecución Free vs Pro
- [ ] Documentar mejoras de rendimiento
- [ ] Ajustar índices si es necesario

---

### **FASE 7: Despliegue a Producción** 🚀
**Duración estimada:** 30 minutos  
**Estado:** ⬜ Pendiente

#### 7.1 Preparación Pre-Deployment
- [ ] Backup final del proyecto Free (por si acaso)
- [ ] Validar que todos los tests pasan
- [ ] Preparar mensaje de mantenimiento (si es crítico)
- [ ] Notificar a usuarios clave (opcional)

#### 7.2 Deployment en Render
```bash
# En Dashboard de Render:
1. Ir a Environment Variables
2. Actualizar DATABASE_URL con la nueva URL Pro
3. Click "Save Changes"
4. Render hará auto-redeploy
```

- [ ] Actualizar `DATABASE_URL` en Render
- [ ] Esperar que termine el deploy (~3-5 minutos)
- [ ] Monitorear logs: `https://dashboard.render.com/[tu-proyecto]/logs`

#### 7.3 Validación Post-Deployment
- [ ] Acceder a `https://tu-app.onrender.com`
- [ ] Login con Google OAuth
- [ ] Navegar a `/analytics`
- [ ] Verificar que los datos históricos están presentes
- [ ] Realizar 2-3 navegaciones para generar nuevos logs
- [ ] Verificar en Supabase Pro que se están insertando nuevos registros

#### 7.4 Monitoreo Inicial (primeras 24 horas)
- [ ] Revisar logs de Render cada 2 horas
- [ ] Verificar en Supabase Pro Dashboard:
  - Database Health
  - Query Performance
  - Número de conexiones activas
- [ ] Revisar errores en logs de aplicación
- [ ] Confirmar que no hay errores de conexión

---

## ✅ Checklist de Rollback (Plan B)

Si algo sale mal durante la migración:

### Rollback Inmediato (en producción)
1. [ ] Ir a Render → Environment Variables
2. [ ] Cambiar `DATABASE_URL` de vuelta al proyecto Free antiguo
3. [ ] Guardar y esperar redeploy automático
4. [ ] Verificar que la app funciona con la DB antigua

### Rollback Local
1. [ ] Restaurar `.env` con `DATABASE_URL` antiguo
2. [ ] Reiniciar app: `python app.py`
3. [ ] Verificar funcionalidad

---

## 📊 Beneficios Esperados del Plan Pro

### Mejoras de Rendimiento
- ✅ **8 GB RAM** vs 500 MB (Free) = 16x más memoria
- ✅ **2 CPU dedicados** vs compartidos
- ✅ **8 GB Storage** vs 500 MB
- ✅ **100 GB Bandwidth** vs 2 GB
- ✅ **60 conexiones concurrentes** vs 50 (con pooling)

### Nuevas Capacidades
- ✅ **Point-in-time Recovery** (PITR) - Backup cada 2 segundos
- ✅ **7 días de backups** vs 24 horas
- ✅ **Database webhooks** (notificaciones en tiempo real)
- ✅ **Read replicas** (para escalabilidad futura)
- ✅ **Custom domains** para Supabase API
- ✅ **Soporte prioritario** por email

### Monitoreo Avanzado
- ✅ **Query performance insights**
- ✅ **Slow query log**
- ✅ **Database observability**
- ✅ **Custom alertas**

---

## 💰 Costos y Consideraciones

### Costo Mensual
- **Supabase Pro:** $25/mes
- **Render (si aplica):** Según plan actual
- **Total estimado:** $25-50/mes

### ROI Esperado
- **Tiempo ahorrado en troubleshooting:** ~2 horas/mes ($40-100 valor)
- **Mejora en uptime:** 99.9% SLA
- **Reducción de errores por límites:** Priceless 😄

---

## 🔐 Seguridad y Compliance

### Checklist de Seguridad
- [ ] Passwords almacenados en gestor de contraseñas
- [ ] Acceso a Supabase con 2FA habilitado
- [ ] **No exponer credenciales** en código o logs
- [ ] Rotar password del proyecto Free después de migrar
- [ ] Configurar IP Allowlist en Supabase Pro (opcional)
- [ ] Implementar Row Level Security (RLS) si es necesario

---

## 📝 Timeline Estimado

| Fase | Tiempo | Día Sugerido |
|------|--------|--------------|
| Preparación y Análisis | 1h | Día 1 - Mañana |
| Creación Proyecto Pro | 30m | Día 1 - Tarde |
| Recreación Estructura | 30m | Día 1 - Tarde |
| Migración de Datos | 1-2h | Día 2 - Mañana |
| Actualización de Código | 30m | Día 2 - Tarde |
| Testing y Validación | 1h | Día 2 - Tarde |
| Despliegue Producción | 30m | Día 3 - Mañana |

**Total estimado:** 5-6 horas distribuidas en 2-3 días

---

## 🆘 Recursos y Contactos

### Documentación Oficial
- [Supabase Migrations Guide](https://supabase.com/docs/guides/getting-started/migrate-data)
- [PostgreSQL pg_dump](https://www.postgresql.org/docs/current/app-pgdump.html)
- [Supabase Pro Features](https://supabase.com/pricing)

### Comandos Útiles
```bash
# Ver tamaño de tabla
SELECT pg_size_pretty(pg_total_relation_size('page_visits'));

# Ver número de filas
SELECT COUNT(*) FROM page_visits;

# Ver últimos 10 registros
SELECT * FROM page_visits ORDER BY visit_timestamp DESC LIMIT 10;

# Verificar conexiones activas
SELECT count(*) FROM pg_stat_activity;
```

### Troubleshooting Común
| Problema | Solución |
|----------|----------|
| "Connection refused" | Verificar que IP está whitelisted en Supabase |
| "Too many clients" | Usar Transaction mode (puerto 6543) en vez de Session mode |
| "Password authentication failed" | Verificar que el password en `DATABASE_URL` es correcto |
| Slow queries | Ejecutar `ANALYZE page_visits;` para actualizar estadísticas |

---

## 📸 Evidencias (Completar Durante Migración)

### Pre-Migración
- [ ] Screenshot de count en proyecto Free
- [ ] Screenshot de tamaño de DB en Free
- [ ] Screenshot de configuración actual

### Post-Migración
- [ ] Screenshot de count en proyecto Pro
- [ ] Screenshot de tamaño de DB en Pro
- [ ] Screenshot de panel de analytics funcionando
- [ ] Screenshot de Database Health en Supabase Pro

---

## ✍️ Log de Ejecución

| Fecha | Fase | Acción | Resultado | Notas |
|-------|------|--------|-----------|-------|
| - | - | - | - | Completar durante la migración |

---

## 🎯 Próximos Pasos (Post-Migración)

### Inmediato (Semana 1)
- [ ] Monitorear performance por 7 días
- [ ] Documentar cualquier issue
- [ ] Ajustar índices si es necesario
- [ ] Configurar alertas en Supabase (umbral de conexiones, storage)

### Corto Plazo (Mes 1)
- [ ] Implementar Point-in-time Recovery (PITR)
- [ ] Configurar webhooks si son útiles
- [ ] Optimizar queries lentas identificadas
- [ ] Explorar Database Observability features

### Medio Plazo (Mes 3)
- [ ] Evaluar implementar Row Level Security (RLS)
- [ ] Considerar read replicas si el tráfico aumenta
- [ ] Crear dashboard de métricas de DB
- [ ] Revisar costos vs uso real

### Largo Plazo (Mes 6+)
- [ ] Evaluar migración a plan Team si crece el equipo
- [ ] Implementar data archiving para datos antiguos
- [ ] Evaluar analytics avanzados (BI integration)
- [ ] Considerar multi-región si hay usuarios globales

---

## 🔒 Desactivación del Proyecto Free (DESPUÉS de validar Pro)

**⚠️ IMPORTANTE: Esperar al menos 7 días después de migrar antes de eliminar el proyecto Free**

Una vez confirmado que todo funciona en Pro:

1. [ ] **Backup final del proyecto Free:**
   ```bash
   pg_dump -h aws-0-us-west-1.pooler.supabase.com \
           -U postgres.ppmbwujtfueilifisxhs \
           -p 6543 \
           -d postgres \
           --clean --if-exists \
           -f FINAL_BACKUP_free_$(date +%Y%m%d).sql
   ```

2. [ ] Guardar backup en:
   - Local: `backups/`
   - Cloud: Google Drive / Dropbox
   - GitHub (repo privado): Como artifact

3. [ ] **Pausar el proyecto Free** (no eliminar todavía):
   - Ir a Settings → General
   - Click "Pause Project"
   - Esperar 30 días más

4. [ ] **Eliminar proyecto Free** (después de 30 días):
   - Ir a Settings → General
   - Scroll hasta "Danger Zone"
   - Click "Delete project"
   - Confirmar escribiendo el nombre del proyecto

---

**Documento creado:** 1 de abril de 2026  
**Última actualización:** 1 de abril de 2026  
**Estado:** 📋 Planificación completa - Listo para ejecutar  
**Próxima revisión:** Después de completar cada fase

---

*Este plan es living document. Actualizar conforme se ejecute la migración.*
