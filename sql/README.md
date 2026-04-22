# 🗄️ SQL Scripts

Scripts SQL para creación de tablas, migraciones y mantenimiento de base de datos.

## Archivos

### `create_analytics_table.sql`
Script DDL para crear la tabla `page_visits` en Supabase PostgreSQL.

**Descripción:**
- Tabla para almacenar métricas de visitas a páginas
- Incluye índices optimizados para consultas frecuentes
- Políticas RLS (Row Level Security) configuradas

**Campos:**
- `id` - UUID primary key
- `user_email` - Email del usuario autenticado
- `page_name` - Nombre de la página visitada
- `ip_address` - IP del visitante
- `user_agent` - User agent del navegador
- `referer` - URL de referencia
- `method` - Método HTTP (GET, POST)
- `created_at` - Timestamp de la visita

**Uso:**
```sql
-- Ejecutar en Supabase SQL Editor
\i sql/create_analytics_table.sql
```

---

### `migrate_supabase_pro.sql`
Script de migración completo para Supabase Pro.

**Descripción:**
- Crea esquema completo de analytics
- Configura RLS policies
- Crea índices optimizados
- Incluye funciones auxiliares

**Uso:**
```bash
# Ejecutar con psql
psql -h db.xxxxx.supabase.co -U postgres -d postgres -f sql/migrate_supabase_pro.sql

# O en Supabase Dashboard > SQL Editor
# Copiar y ejecutar el contenido del archivo
```

**Requisitos:**
- Proyecto Supabase Pro activo
- Credenciales de superusuario
- Variables de entorno configuradas

**Referencias:** Ver [docs/PLAN_MIGRACION_SUPABASE_PRO.md](../docs/PLAN_MIGRACION_SUPABASE_PRO.md)

---

## Estructura

```
sql/
├── README.md                        # Este archivo
├── create_analytics_table.sql      # Creación tabla analytics
└── migrate_supabase_pro.sql        # Migración completa a Pro
```

## Notas de Seguridad

- ⚠️ Revisar scripts antes de ejecutar en producción
- 🔐 No commitear credenciales en archivos SQL
- 📊 Hacer backup antes de ejecutar migraciones
- ✅ Validar con `scripts/validate_migration.py` después de migrar

## Conexión a Supabase

```bash
# Formato de connection string
postgresql://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres
```

Variables requeridas:
- `DATABASE_URL` - URL de conexión completa
- `SUPABASE_URL` - URL del proyecto Supabase
- `SUPABASE_KEY` - API key anónima (opcional para queries directas)
