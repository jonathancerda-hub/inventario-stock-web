-- =====================================================
-- SCRIPT SQL: Tablas para Módulo de Administración
-- =====================================================
-- Proyecto: Inventario Stock
-- Base de Datos: Supabase PostgreSQL
-- Fecha: 21 de abril de 2026
-- =====================================================

-- =====================================================

-- Tabla: inventario_user_permissions
-- Almacena usuarios, roles y permisos del sistema de inventario
CREATE TABLE inventario_user_permissions (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    role VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by VARCHAR(255),
    last_login TIMESTAMPTZ
);

-- Índices para optimización
CREATE INDEX IF NOT EXISTS idx_inv_user_role ON inventario_user_permissions(role);
CREATE INDEX IF NOT EXISTS idx_inv_user_active ON inventario_user_permissions(is_active);
CREATE INDEX IF NOT EXISTS idx_inv_user_email ON inventario_user_permissions(email);

-- Comentarios
COMMENT ON TABLE inventario_user_permissions IS 'Usuarios y roles del sistema de inventario';
COMMENT ON COLUMN inventario_user_permissions.email IS 'Email corporativo del usuario (@agrovetmarket.com)';
COMMENT ON COLUMN inventario_user_permissions.role IS 'Rol: admin_full, dashboard_user, inventory_user, viewer';
COMMENT ON COLUMN inventario_user_permissions.is_active IS 'Estado del usuario (soft delete)';

-- =====================================================

-- Tabla: inventario_audit_log
-- Registro de auditoría de cambios en permisos del sistema de inventario
CREATE TABLE inventario_audit_log (
    id BIGSERIAL PRIMARY KEY,
    action VARCHAR(50) NOT NULL,
    user_email VARCHAR(255) NOT NULL,
    performed_by VARCHAR(255) NOT NULL,
    details JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para optimización
CREATE INDEX IF NOT EXISTS idx_inv_audit_timestamp ON inventario_audit_log(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_inv_audit_action ON inventario_audit_log(action);
CREATE INDEX IF NOT EXISTS idx_inv_audit_user ON inventario_audit_log(user_email);
CREATE INDEX IF NOT EXISTS idx_inv_audit_performed_by ON inventario_audit_log(performed_by);

-- Comentarios
COMMENT ON TABLE inventario_audit_log IS 'Auditoría de cambios en permisos y usuarios del sistema de inventario';
COMMENT ON COLUMN inventario_audit_log.action IS 'Tipo de acción: user_created, user_updated, user_deleted, user_reactivated, role_changed';
COMMENT ON COLUMN inventario_audit_log.details IS 'Detalles en JSON (valores anteriores, nuevos, etc.)';
COMMENT ON COLUMN inventario_audit_log.ip_address IS 'Dirección IP desde donde se realizó la acción';

-- =====================================================

-- Insertar usuarios iniciales desde roles.json
-- Administradores
INSERT INTO inventario_user_permissions (email, role, created_by, is_active)
VALUES 
    ('jonathan.cerda@agrovetmarket.com', 'admin_full', 'sistema_migracion', TRUE),
    ('ena.fernandez@agrovetmarket.com', 'admin_full', 'sistema_migracion', TRUE)
ON CONFLICT (email) DO UPDATE SET
    role = EXCLUDED.role,
    updated_at = NOW();

-- Dashboard users
INSERT INTO inventario_user_permissions (email, role, created_by, is_active)
VALUES 
    ('umberto.calderon@agrovetmarket.com', 'dashboard_user', 'sistema_migracion', TRUE),
    ('sandra.meneses@agrovetmarket.com', 'dashboard_user', 'sistema_migracion', TRUE),
    ('jimena.delrisco@agrovetmarket.com', 'dashboard_user', 'sistema_migracion', TRUE),
    ('johanna.hurtado@agrovetmarket.com', 'dashboard_user', 'sistema_migracion', TRUE),
    ('milady.alvarez@agrovetmarket.com', 'dashboard_user', 'sistema_migracion', TRUE),
    ('giovanna.anchorena@agrovetmarket.com', 'dashboard_user', 'sistema_migracion', TRUE)
ON CONFLICT (email) DO UPDATE SET
    role = EXCLUDED.role,
    updated_at = NOW();

-- Resto de usuarios de whitelist como viewers
INSERT INTO inventario_user_permissions (email, role, created_by, is_active)
SELECT 
    TRIM(email_line) as email,
    'viewer' as role,
    'sistema_migracion' as created_by,
    TRUE as is_active
FROM (
    VALUES
        ('juancarlos.campos@agrovetmarket.com'),
        ('katherine.navarro@agrovetmarket.com'),
        ('regina.martinez@agrovetmarket.com'),
        ('juan.portal@agrovetmarket.com'),
        ('manuel.bravo@agrovetmarket.com'),
        ('stephanie.hiyagon@agrovetmarket.com'),
        ('carolina.tasayco@agrovetmarket.com'),
        ('luis.chavez@agrovetmarket.com'),
        ('thalia.grillo@agrovetmarket.com'),
        ('jose.delgado@agrovetmarket.com'),
        ('karina.guillen@agrovetmarket.com'),
        ('dagoberto.salazar@agrovetmarket.com'),
        ('samire.huaman@agrovetmarket.com'),
        ('carmen.morales@agrovetmarket.com'),
        ('vanessa.parker@agrovetmarket.com'),
        ('miguel.hernandez@agrovetmarket.com'),
        ('stefanny.rios@agrovetmarket.com'),
        ('maria.angulo@agrovetmarket.com'),
        ('flavia.mendoza@agrovetmarket.com'),
        ('ariana.carmona@agrovetmarket.com'),
        ('julian.larosa@agrovetmarket.com'),
        ('jonathan.reyes@agrovetmarket.com'),
        ('omar.chavez@agrovetmarket.com'),
        ('lelia.sanchez@agrovetmarket.com'),
        ('sandra.krklec@agrovetmarket.com'),
        ('orlando.jaimes@agrovetmarket.com'),
        ('cusi.flores@agrovetmarket.com'),
        ('janet.hueza@agrovetmarket.com'),
        ('perci.mondragon@agrovetmarket.com')
) AS emails(email_line)
WHERE TRIM(email_line) NOT IN (
    SELECT email FROM inventario_user_permissions
)
ON CONFLICT (email) DO NOTHING;

-- =====================================================

-- Registrar migración en audit log
INSERT INTO inventario_audit_log (action, user_email, performed_by, details)
VALUES (
    'migration_completed',
    'sistema',
    'sistema_migracion',
    jsonb_build_object(
        'message', 'Migración inicial de usuarios desde roles.json y whitelist.txt',
        'total_users', (SELECT COUNT(*) FROM inventario_user_permissions),
        'timestamp', NOW()
    )
);

-- =====================================================

-- Verificación
SELECT 
    role,
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE is_active = TRUE) as activos
FROM inventario_user_permissions
GROUP BY role
ORDER BY role;

-- =====================================================
-- FIN DEL SCRIPT
-- =====================================================
