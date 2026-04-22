# Guía Rápida: Migración a Supabase Pro

## 📦 Archivos de Este Kit de Migración

| Archivo | Propósito |
|---------|-----------|
| `PLAN_MIGRACION_SUPABASE_PRO.md` | Plan completo detallado (7 fases) |
| `migrate_supabase_pro.sql` | Script SQL para crear estructura en Pro |
| `migrate_data_to_pro.py` | Script Python para migrar datos (opcional) |
| `validate_migration.py` | Script de validación post-migración |
| `MIGRACION_README.md` | Esta guía rápida |

---

## ⚡ Quick Start (30 minutos)

### 1️⃣ Backup del Proyecto Actual (5 min)

```bash
# Crear directorio de backups
mkdir -p backups

# Backup completo
pg_dump -h aws-0-us-west-1.pooler.supabase.com \
        -U postgres.ppmbwujtfueilifisxhs \
        -p 6543 \
        -d postgres \
        -t page_visits \
        --no-owner --no-acl \
        -f backups/backup_$(date +%Y%m%d_%H%M%S).sql

# Verificar backup
ls -lh backups/
```

### 2️⃣ Crear Proyecto Pro en Supabase (10 min)

1. Ir a [supabase.com/dashboard](https://supabase.com/dashboard)
2. Click **"New Project"**
3. Configurar:
   - **Name:** `inventario-stock-pro`
   - **Password:** Generar seguro (guardar en password manager)
   - **Region:** `us-east-1` (o la más cercana a Render)
   - **Plan:** Pro ($25/mes)
4. Esperar ~2 minutos
5. Ir a **Settings → Database**
6. Copiar **Connection Pooler URL** (puerto 6543):
   ```
   postgresql://postgres.[REF]:[PASS]@aws-0-[REGION].pooler.supabase.com:6543/postgres
   ```

### 3️⃣ Crear Estructura en Pro (2 min)

1. En Supabase Pro Dashboard → **SQL Editor**
2. Abrir el archivo `migrate_supabase_pro.sql`
3. Copiar todo el contenido
4. Pegar en SQL Editor
5. Click **"Run"**
6. Verificar mensaje: ✅ Tabla creada exitosamente

### 4️⃣ Migrar Datos (10 min)

**Opción A: pg_dump (Recomendado)**

```bash
# 1. Exportar solo datos
pg_dump -h aws-0-us-west-1.pooler.supabase.com \
        -U postgres.ppmbwujtfueilifisxhs \
        -p 6543 \
        -d postgres \
        -t page_visits \
        --data-only \
        --no-owner --no-acl \
        -f backups/data_only.sql

# 2. Importar al proyecto Pro
psql -h aws-0-[NEW_REGION].pooler.supabase.com \
     -U postgres.[NEW_PROJECT_REF] \
     -p 6543 \
     -d postgres \
     -f backups/data_only.sql

# 3. Verificar
psql -h aws-0-[NEW_REGION].pooler.supabase.com \
     -U postgres.[NEW_PROJECT_REF] \
     -p 6543 \
     -d postgres \
     -c "SELECT COUNT(*) FROM page_visits;"
```

**Opción B: Script Python (si Opción A falla)**

```bash
# 1. Editar migrate_data_to_pro.py con las URLs correctas
nano migrate_data_to_pro.py  # o usar VS Code

# 2. Ejecutar
python migrate_data_to_pro.py

# 3. Seguir instrucciones en pantalla
```

### 5️⃣ Validar Migración (3 min)

```bash
# Ejecutar script de validación
python validate_migration.py

# O validación manual en SQL
psql -h [PRO_URL] -c "
SELECT 
    COUNT(*) as total_filas,
    COUNT(DISTINCT user_email) as usuarios_unicos,
    MIN(visit_timestamp) as primera_visita,
    MAX(visit_timestamp) as ultima_visita
FROM page_visits;
"
```

---

## 🔧 Actualizar Aplicación

### Local (.env)

```bash
# Editar .env
nano .env
```

Cambiar:
```env
DATABASE_URL=postgresql://postgres.[NEW_REF]:[NEW_PASS]@aws-0-[NEW_REGION].pooler.supabase.com:6543/postgres
```

### Render (Producción)

1. Ir a [Dashboard de Render](https://dashboard.render.com/)
2. Seleccionar tu servicio
3. **Environment** tab
4. Editar `DATABASE_URL` con la nueva URL
5. Click **"Save Changes"**
6. Esperar auto-deploy (~3 min)
7. Verificar logs

---

## ✅ Checklist Post-Migración

- [ ] Backup del proyecto Free guardado localmente
- [ ] Proyecto Pro creado correctamente
- [ ] Tabla `page_visits` creada en Pro
- [ ] Datos migrados (count coincide)
- [ ] Validación ejecutada sin errores
- [ ] `.env` local actualizado
- [ ] Render Environment actualizado
- [ ] App funciona en local con Pro
- [ ] App funciona en producción con Pro
- [ ] Dashboard `/analytics` muestra datos históricos
- [ ] Monitoreo activo por 7 días
- [ ] Proyecto Free pausado (después de 7 días)

---

## 🆘 Troubleshooting

### Error: "Connection refused"
```bash
# Solución: Verificar URL y puerto
# Session mode: puerto 5432
# Transaction mode: puerto 6543 (recomendado)
```

### Error: "Too many clients"
```bash
# Solución: Usar Transaction mode (6543) en vez de Session mode (5432)
```

### Error: "Password authentication failed"
```bash
# Solución: Regenerar password en Supabase
# Settings → Database → Reset Database Password
```

### Count no coincide
```bash
# Solución: Re-ejecutar migración
# 1. Truncar tabla en Pro: TRUNCATE page_visits RESTART IDENTITY;
# 2. Repetir paso 4 de migración
```

---

## 📊 Comandos Útiles

### Verificar Estado de la DB

```sql
-- Total de filas
SELECT COUNT(*) FROM page_visits;

-- Usuarios únicos
SELECT COUNT(DISTINCT user_email) FROM page_visits;

-- Tamaño de tabla + índices
SELECT pg_size_pretty(pg_total_relation_size('page_visits'));

-- Últimas 10 visitas
SELECT * FROM page_visits ORDER BY visit_timestamp DESC LIMIT 10;

-- Conexiones activas
SELECT count(*) FROM pg_stat_activity;
```

### Optimizar Performance

```sql
-- Actualizar estadísticas
ANALYZE page_visits;

-- Reindexar
REINDEX TABLE page_visits;

-- Ver índices no usados
SELECT * FROM pg_stat_user_indexes 
WHERE schemaname = 'public' 
  AND idx_scan = 0;
```

---

## 🔐 Rollback (Si algo sale mal)

### Revertir en Local
```bash
# .env
DATABASE_URL=[URL_DEL_PROYECTO_FREE_ANTIGUO]
```

### Revertir en Render
1. Environment → Edit `DATABASE_URL`
2. Poner URL del proyecto Free
3. Save → Auto-redeploy

---

## 📞 Soporte

- **Documentación Completa:** `docs/PLAN_MIGRACION_SUPABASE_PRO.md`
- **Supabase Docs:** https://supabase.com/docs
- **PostgreSQL pg_dump:** https://www.postgresql.org/docs/current/app-pgdump.html

---

## 🎯 Timeline Sugerido

| Día | Actividad |
|-----|-----------|
| **Día 1 AM** | Backup + Crear proyecto Pro + Crear estructura |
| **Día 1 PM** | Migrar datos + Validar |
| **Día 2 AM** | Actualizar código + Testing local |
| **Día 2 PM** | Deploy a producción + Monitorear |
| **Día 3-9** | Monitoreo pasivo |
| **Día 10** | Pausar proyecto Free |
| **Día 40** | Eliminar proyecto Free |

---

**Última actualización:** 1 de abril de 2026  
**Autor:** Jonathan Cerda  
**Estado:** ✅ Listo para ejecutar
