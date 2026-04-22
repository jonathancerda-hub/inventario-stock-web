-- ============================================
-- SCRIPT DE MIGRACIÓN - SUPABASE PRO
-- ============================================
-- Proyecto: Inventario Stock Web
-- Fecha: 2026-04-01
-- Tier: Supabase Pro
-- Propósito: Crear estructura optimizada en nuevo proyecto Pro
-- ============================================

-- Configurar timezone
SET timezone = 'America/Lima';

-- Verificar version de PostgreSQL
SELECT version();

-- ============================================
-- TABLA: page_visits (Analytics de usuarios)
-- ============================================

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
    
    -- Columnas adicionales para Supabase Pro
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- ÍNDICES (Optimizados para analytics)
-- ============================================

-- Índice para búsquedas por usuario
CREATE INDEX IF NOT EXISTS idx_visits_user 
ON page_visits(user_email);

-- Índice para consultas por fecha (DESC = más recientes primero)
CREATE INDEX IF NOT EXISTS idx_visits_timestamp 
ON page_visits(visit_timestamp DESC);

-- Índice para análisis por página
CREATE INDEX IF NOT EXISTS idx_visits_page 
ON page_visits(page_url);

-- Índice para created_at (monitoreo de inserciones)
CREATE INDEX IF NOT EXISTS idx_visits_created_at 
ON page_visits(created_at DESC);

-- Índices compuestos (mejora queries complejas)
CREATE INDEX IF NOT EXISTS idx_visits_user_timestamp 
ON page_visits(user_email, visit_timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_visits_page_timestamp 
ON page_visits(page_url, visit_timestamp DESC);

-- Índice parcial: solo visitas recientes (últimos 90 días)
CREATE INDEX IF NOT EXISTS idx_visits_recent 
ON page_visits(visit_timestamp DESC)
WHERE visit_timestamp > CURRENT_TIMESTAMP - INTERVAL '90 days';

-- ============================================
-- COMENTARIOS (Documentación inline)
-- ============================================

COMMENT ON TABLE page_visits 
IS 'Registro de visitas de usuarios al sistema inventario-stock. Almacena analytics de navegación para métricas y monitoreo. Migrado a Supabase Pro el 2026-04-01.';

COMMENT ON COLUMN page_visits.id 
IS 'ID autoincremental único de cada visita';

COMMENT ON COLUMN page_visits.user_email 
IS 'Email del usuario autenticado vía Google OAuth';

COMMENT ON COLUMN page_visits.user_name 
IS 'Nombre completo del usuario de Google';

COMMENT ON COLUMN page_visits.page_url 
IS 'URL completa de la página visitada';

COMMENT ON COLUMN page_visits.page_title 
IS 'Título de la página o endpoint de Flask';

COMMENT ON COLUMN page_visits.visit_timestamp 
IS 'Timestamp de la visita en timezone America/Lima';

COMMENT ON COLUMN page_visits.session_duration 
IS 'Duración de la sesión en segundos (experimental, actualmente siempre 0)';

COMMENT ON COLUMN page_visits.ip_address 
IS 'Dirección IP del cliente (X-Forwarded-For en Render)';

COMMENT ON COLUMN page_visits.user_agent 
IS 'User-Agent del navegador del usuario';

COMMENT ON COLUMN page_visits.referrer 
IS 'URL de referencia (página anterior)';

COMMENT ON COLUMN page_visits.method 
IS 'Método HTTP de la request (GET, POST, etc)';

COMMENT ON COLUMN page_visits.created_at 
IS 'Timestamp de creación del registro (inmutable)';

COMMENT ON COLUMN page_visits.updated_at 
IS 'Timestamp de última actualización del registro (auto-actualizado por trigger)';

-- ============================================
-- FUNCIÓN: Auto-actualizar updated_at
-- ============================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION update_updated_at_column() 
IS 'Función de trigger que actualiza automáticamente la columna updated_at al modificar un registro';

-- ============================================
-- TRIGGER: Actualizar updated_at en UPDATE
-- ============================================

CREATE TRIGGER update_page_visits_updated_at
    BEFORE UPDATE ON page_visits
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TRIGGER update_page_visits_updated_at ON page_visits 
IS 'Trigger que actualiza updated_at antes de cada UPDATE en page_visits';

-- ============================================
-- SEGURIDAD: Row Level Security (RLS)
-- ============================================
-- NOTA: RLS está deshabilitado por defecto.
-- Descomentar si se requiere control de acceso a nivel de fila en el futuro.

-- ALTER TABLE page_visits ENABLE ROW LEVEL SECURITY;

-- -- Política: Usuarios solo ven sus propias visitas
-- CREATE POLICY users_view_own_visits ON page_visits
--     FOR SELECT
--     USING (auth.jwt() ->> 'email' = user_email);

-- -- Política: Admins ven todo
-- CREATE POLICY admins_view_all_visits ON page_visits
--     FOR SELECT
--     USING (
--         auth.jwt() ->> 'email' IN (
--             'admin@agrovetmarket.com',
--             'jonathan.cerda@agrovetmarket.com'
--         )
--     );

-- ============================================
-- VALIDACIÓN POST-CREACIÓN
-- ============================================

-- Verificar que la tabla se creó correctamente
SELECT 
    'page_visits' as tabla,
    COUNT(*) as total_columnas,
    pg_size_pretty(pg_total_relation_size('page_visits')) as tamaño
FROM information_schema.columns 
WHERE table_name = 'page_visits';

-- Listar todas las columnas
SELECT 
    column_name,
    data_type,
    character_maximum_length,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'page_visits'
ORDER BY ordinal_position;

-- Verificar índices creados
SELECT 
    indexname as indice,
    indexdef as definicion
FROM pg_indexes 
WHERE tablename = 'page_visits'
ORDER BY indexname;

-- Verificar triggers
SELECT 
    trigger_name,
    event_manipulation,
    event_object_table,
    action_statement
FROM information_schema.triggers
WHERE event_object_table = 'page_visits';

-- Verificar comentarios
SELECT 
    objsubid,
    description
FROM pg_description
WHERE objoid = 'page_visits'::regclass
ORDER BY objsubid;

-- ============================================
-- QUERIES DE PRUEBA (Opcional)
-- ============================================

-- Insertar registro de prueba
INSERT INTO page_visits (user_email, user_name, page_url, page_title)
VALUES ('test@example.com', 'Test User', '/dashboard', 'dashboard');

-- Verificar inserción
SELECT * FROM page_visits WHERE user_email = 'test@example.com';

-- Limpiar registro de prueba
DELETE FROM page_visits WHERE user_email = 'test@example.com';

-- ============================================
-- OPTIMIZACIONES ADICIONALES (Pro features)
-- ============================================

-- Actualizar estadísticas de la tabla (mejora query planner)
ANALYZE page_visits;

-- Reindexar (necesario si hay datos migrados)
-- REINDEX TABLE page_visits;

-- Vacuum (limpiar espacio no usado)
-- VACUUM ANALYZE page_visits;

-- ============================================
-- MONITOREO (Queries útiles para Supabase Pro)
-- ============================================

-- Ver queries más lentas en esta tabla
-- SELECT * FROM pg_stat_statements 
-- WHERE query LIKE '%page_visits%'
-- ORDER BY mean_exec_time DESC
-- LIMIT 10;

-- Ver tamaño detallado de tabla e índices
SELECT
    'page_visits' as tabla,
    pg_size_pretty(pg_relation_size('page_visits')) as tabla_size,
    pg_size_pretty(pg_indexes_size('page_visits')) as indices_size,
    pg_size_pretty(pg_total_relation_size('page_visits')) as total_size;

-- Ver estadísticas de uso de índices
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan as veces_usado,
    idx_tup_read as filas_leidas,
    idx_tup_fetch as filas_obtenidas
FROM pg_stat_user_indexes
WHERE tablename = 'page_visits'
ORDER BY idx_scan DESC;

-- ============================================
-- SCRIPT COMPLETADO
-- ============================================

SELECT 
    '✅ Migración completada exitosamente' as status,
    CURRENT_TIMESTAMP as timestamp,
    version() as postgresql_version;

-- ============================================
-- NOTAS FINALES
-- ============================================
-- 1. Este script crea la estructura optimizada para Supabase Pro
-- 2. Los datos deben migrarse por separado (ver PLAN_MIGRACION_SUPABASE_PRO.md)
-- 3. Después de migrar datos, ejecutar: ANALYZE page_visits;
-- 4. Monitorear performance en Supabase Dashboard > Database > Query Performance
-- 5. Configurar alertas para: storage usage, connection count, slow queries
-- 
-- Contacto: Jonathan Cerda
-- Proyecto: inventario-stock-web
-- Documentación: docs/PLAN_MIGRACION_SUPABASE_PRO.md
-- ============================================
