-- ============================================
-- SCRIPT DE MIGRACIÓN - ANALYTICS INVENTARIO
-- ============================================
-- Proyecto: Inventario Stock Web
-- Base de datos: Supabase PostgreSQL
-- Project Ref: ppmbwujtfueilifisxhs
-- ============================================

-- Crear tabla de visitas de usuarios
CREATE TABLE IF NOT EXISTS page_visits (
    id SERIAL PRIMARY KEY,
    user_email VARCHAR(255),
    user_name VARCHAR(255),
    page_url VARCHAR(500),
    page_title VARCHAR(255),
    visit_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    ip_address VARCHAR(100),
    user_agent TEXT,
    referrer VARCHAR(500),
    method VARCHAR(10)
);

-- Índices para optimizar consultas
CREATE INDEX IF NOT EXISTS idx_visits_user ON page_visits(user_email);
CREATE INDEX IF NOT EXISTS idx_visits_timestamp ON page_visits(visit_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_visits_page ON page_visits(page_url);

-- Documentación de la tabla
COMMENT ON TABLE page_visits IS 'Registro de visitas de usuarios al sistema de inventario-stock';

-- Verificar creación
SELECT 
    'Tabla creada exitosamente' as status,
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
