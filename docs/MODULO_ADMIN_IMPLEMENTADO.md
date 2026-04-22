# =====================================================
# MÓDULO DE ADMINISTRACIÓN DE PERMISOS - INVENTARIO
# =====================================================
# Fecha: 21 de abril de 2026
# Proyecto: Sistema de Inventario con Odoo y Supabase
# =====================================================

## 📋 RESUMEN DE IMPLEMENTACIÓN

Se ha implementado un módulo completo de administración de usuarios y permisos 
integrado con Supabase PostgreSQL, siguiendo las mejores prácticas de seguridad 
OWASP y arquitectura similar a Dashboard-Ventas-Backup.

---

## 🗂️ ESTRUCTURA DE ARCHIVOS CREADOS

### **Backend (Python)**
- `permissions_manager.py` - Gestor de permisos y roles (CRUD completo)
- `audit_logger.py` - Sistema de auditoría con tracking de IP y user agent

### **Base de Datos (SQL)**
- `sql/create_admin_tables.sql` - Script de creación de tablas:
  * `inventario_user_permissions` - Usuarios, roles y permisos
  * `inventario_audit_log` - Historial de cambios completo

### **Frontend (HTML Templates)**
- `templates/admin/users_list.html` - Lista de usuarios con DataTables
- `templates/admin/user_add.html` - Formulario de creación
- `templates/admin/user_edit.html` - Formulario de edición con preview
- `templates/admin/audit_log.html` - Historial de auditoría

### **Rutas Flask (app.py)**
- `GET /admin/users` - Lista de usuarios
- `GET/POST /admin/users/add` - Agregar usuario
- `GET/POST /admin/users/edit/<email>` - Editar rol
- `POST /admin/users/delete/<email>` - Desactivar usuario (soft delete)
- `POST /admin/users/reactivate/<email>` - Reactivar usuario
- `GET /admin/audit-log` - Historial de auditoría

---

## 🛡️ SISTEMA DE ROLES Y PERMISOS

### **Roles Disponibles:**

| Rol | Descripción | Permisos |
|-----|-------------|----------|
| **admin_full** | Acceso completo al sistema | view_inventory, export_inventory, view_dashboard, export_dashboard, view_analytics, manage_users, view_audit_log, manage_settings |
| **dashboard_user** | Acceso a dashboard y analytics | view_inventory, export_inventory, view_dashboard, export_dashboard |
| **inventory_user** | Solo inventario | view_inventory, export_inventory |
| **viewer** | Solo visualización | view_inventory |

### **Usuarios Iniciales (migrados desde roles.json):**

**Administradores (2):**
- jonathan.cerda@agrovetmarket.com
- ena.fernandez@agrovetmarket.com

**Dashboard Users (6):**
- umberto.calderon@agrovetmarket.com
- sandra.meneses@agrovetmarket.com
- jimena.delrisco@agrovetmarket.com
- johanna.hurtado@agrovetmarket.com
- milady.alvarez@agrovetmarket.com
- giovanna.anchorena@agrovetmarket.com

**Viewers (29):**
- Resto de usuarios de whitelist.txt

---

## 🔐 CARACTERÍSTICAS DE SEGURIDAD

### **1. Control de Acceso**
- ✅ Decorador `@require_admin(permission)` - Protege todas las rutas admin
- ✅ Verificación de permisos a nivel de usuario
- ✅ Prevención de auto-modificación (no puedes cambiar tu propio rol)
- ✅ Prevención de auto-eliminación

### **2. Auditoría Completa**
- ✅ Registro de todas las operaciones CRUD
- ✅ Tracking de IP address
- ✅ Tracking de User Agent
- ✅ Detalles JSON con valores anteriores y nuevos
- ✅ Timestamp con zona horaria de Perú (America/Lima)

### **3. Soft Delete**
- ✅ No se eliminan usuarios físicamente
- ✅ Campo `is_active` para desactivación
- ✅ Función de reactivación disponible
- ✅ Historial completo preservado

### **4. Validaciones**
- ✅ Email debe ser @agrovetmarket.com
- ✅ Roles válidos predefinidos
- ✅ Confirmación con SweetAlert2 antes de eliminar
- ✅ Preview de permisos al seleccionar rol

---

## 📊 FUNCIONALIDADES DEL MÓDULO

### **Lista de Usuarios** (`/admin/users`)
- Tabla con DataTables (búsqueda, ordenamiento, paginación)
- Estadísticas en cards (activos, inactivos, por rol)
- Filtros por rol y estado
- Badges de colores por rol
- Botones de acción (editar, eliminar, reactivar)

### **Agregar Usuario** (`/admin/users/add`)
- Validación de email corporativo
- Selector de rol con descripción
- Preview dinámico de permisos
- Validación en frontend y backend

### **Editar Usuario** (`/admin/users/edit/<email>`)
- Muestra información actual del usuario
- Comparación de permisos (removidos vs agregados)
- Confirmación con SweetAlert2
- Prevención de auto-modificación

### **Historial de Auditoría** (`/admin/audit-log`)
- Tabla completa con DataTables
- Filtros por acción, usuario, período
- Estadísticas de actividad (últimos 7 días)
- Badges de colores por tipo de acción
- Detalles JSON expandibles

---

## 🚀 INSTRUCCIONES DE DESPLIEGUE

### **1. Ejecutar Script SQL en Supabase**

```bash
# 1. Ve a: https://supabase.com/dashboard/project/ppmbwujtfueilifisxhs/sql
# 2. Copia el contenido de: sql/create_admin_tables.sql
# 3. Pega en el SQL Editor y ejecuta "Run"
```

Esto creará:
- ✅ Tablas `inventario_user_permissions` e `inventario_audit_log`
- ✅ Índices para optimización de consultas
- ✅ Migración automática de 37 usuarios desde roles.json

### **2. Verificar Variables de Entorno**

Asegúrate de tener en `.env`:
```env
DATABASE_URL=postgresql://postgres.ppmbwujtfueilifisxhs:[PASSWORD]@aws-0-us-west-1.pooler.supabase.com:6543/postgres
```

### **3. Instalar Dependencias (si es necesario)**

```bash
pip install psycopg2-binary
```

### **4. Reiniciar Aplicación**

```bash
# Detener app.py (Ctrl+C)
python app.py
```

### **5. Acceder al Módulo Admin**

```
http://localhost:5000/admin/users
```

**Solo usuarios con rol `admin_full` pueden acceder** (jonathan.cerda y ena.fernandez)

---

## 🧪 PRUEBAS RECOMENDADAS

### **Test 1: Acceso al Módulo**
```
1. Login con jonathan.cerda@agrovetmarket.com
2. Ir a Dashboard o Inventario
3. Clic en botón "🔒 Admin" (rojo)
4. Verificar que carga /admin/users
```

### **Test 2: Crear Usuario**
```
1. En /admin/users, clic "Agregar Usuario"
2. Ingresar email: test.usuario@agrovetmarket.com
3. Seleccionar rol: inventory_user
4. Ver preview de permisos
5. Crear usuario
6. Verificar en lista de usuarios
```

### **Test 3: Editar Rol**
```
1. En lista de usuarios, clic "Editar" en test.usuario
2. Cambiar rol a dashboard_user
3. Ver comparación de permisos (removidos vs agregados)
4. Confirmar cambio
5. Verificar badge actualizado
```

### **Test 4: Auditoría**
```
1. Ir a /admin/audit-log
2. Verificar que aparecen las acciones:
   - user_created (test.usuario)
   - role_changed (test.usuario: inventory_user → dashboard_user)
3. Verificar IP address y timestamp
4. Filtrar por action: role_changed
```

### **Test 5: Desactivar Usuario**
```
1. En lista, clic "Desactivar" en test.usuario
2. Confirmar en modal de SweetAlert2
3. Verificar badge cambia a "Inactivo"
4. Ir a audit log y verificar action: user_deleted
```

### **Test 6: Reactivar Usuario**
```
1. En filtros, marcar "Incluir usuarios inactivos"
2. Buscar test.usuario (inactivo)
3. Clic "Reactivar"
4. Verificar badge cambia a "Activo"
5. Verificar en audit log: user_reactivated
```

### **Test 7: Seguridad - Auto-modificación**
```
1. Login con jonathan.cerda@agrovetmarket.com
2. Ir a /admin/users
3. Intentar editar tu propio usuario
4. Verificar error: "No puedes modificar tu propio rol"
```

### **Test 8: Seguridad - Acceso No Autorizado**
```
1. Login con usuario no-admin (ej: umberto.calderon)
2. Intentar acceder a http://localhost:5000/admin/users
3. Verificar Error 403 Forbidden
```

---

## 📈 ESTADÍSTICAS Y MÉTRICAS

El sistema proporciona:

**En Lista de Usuarios:**
- Total de usuarios activos
- Total de usuarios inactivos  
- Usuarios por rol (admin_full, dashboard_user, etc.)

**En Audit Log:**
- Total de acciones (últimos 7 días)
- Usuarios creados
- Roles modificados
- Usuarios desactivados
- Admins más activos
- Usuarios más modificados

---

## 🔄 MIGRACIÓN DE DATOS

### **Estado Actual:**
- ✅ 37 usuarios migrados desde whitelist.txt
- ✅ Roles asignados correctamente desde roles.json
- ✅ Sin pérdida de datos
- ✅ Compatible con sistema anterior

### **Ventajas del Nuevo Sistema:**
1. **Gestión Visual:** Interfaz gráfica vs archivos JSON
2. **Auditoría:** Historial completo de cambios
3. **Escalabilidad:** Base de datos vs archivos planos
4. **Seguridad:** Permisos granulares vs listas simples
5. **Trazabilidad:** IP, user agent, timestamps

---

## 🎨 TECNOLOGÍAS UTILIZADAS

**Backend:**
- Flask 3.1.1
- psycopg2 (PostgreSQL driver)
- python-dotenv

**Frontend:**
- Bootstrap 5
- DataTables (búsqueda y paginación)
- SweetAlert2 (confirmaciones)
- Bootstrap Icons

**Base de Datos:**
- Supabase PostgreSQL
- Índices optimizados
- JSONB para detalles de auditoría

---

## 📝 NOTAS IMPORTANTES

### **Nombres de Tablas:**
- Usamos prefijo `inventario_` para evitar conflictos con otras bases de datos en Supabase
- Tablas: `inventario_user_permissions`, `inventario_audit_log`

### **Zona Horaria:**
- Todos los timestamps en zona horaria de Perú: `America/Lima`
- Manejado automáticamente por pytz

### **Compatibilidad:**
- El sistema anterior (whitelist.txt + roles.json) sigue funcionando
- Los nuevos usuarios solo existen en Supabase
- Migración es transparente para usuarios existentes

---

## 🐛 TROUBLESHOOTING

### **Error: DATABASE_URL no configurada**
```bash
# Verificar .env
cat .env | grep DATABASE_URL

# Si no existe, agregar:
echo 'DATABASE_URL=postgresql://...' >> .env
```

### **Error: Tabla no existe**
```sql
-- Ejecutar en Supabase SQL Editor:
SELECT * FROM inventario_user_permissions LIMIT 1;

-- Si falla, ejecutar nuevamente create_admin_tables.sql
```

### **Error 403 al acceder a /admin/users**
```python
# Verificar rol del usuario en Supabase:
SELECT email, role FROM inventario_user_permissions 
WHERE email = 'tu-email@agrovetmarket.com';

# Debe ser 'admin_full'
```

### **No aparece botón Admin en menú**
```
Solo aparece para usuarios en esta lista hardcodeada:
- jonathan.cerda@agrovetmarket.com
- ena.fernandez@agrovetmarket.com

Para otros admins, acceder directamente a:
http://localhost:5000/admin/users
```

---

## ✅ CHECKLIST DE IMPLEMENTACIÓN

- [x] Script SQL creado y probado
- [x] PermissionsManager implementado
- [x] AuditLogger implementado
- [x] 6 rutas admin en app.py
- [x] 4 templates HTML creados
- [x] Decorador require_admin implementado
- [x] Botones de navegación agregados
- [x] Validaciones frontend (SweetAlert2)
- [x] Validaciones backend (email, rol)
- [x] Soft delete implementado
- [x] Auditoría completa con IP/user agent
- [x] DataTables para búsqueda y paginación
- [x] Estadísticas y métricas
- [x] Documentación completa

---

## 🎯 PRÓXIMOS PASOS (Opcional)

1. **Dashboard de Analytics Admin:**
   - Gráficos de actividad de usuarios
   - Tendencias de cambios de roles
   - Usuarios más activos por período

2. **Exportación de Auditoría:**
   - Exportar logs a Excel
   - Filtros avanzados por fecha
   - Búsqueda por IP address

3. **Notificaciones:**
   - Email al crear/modificar usuarios
   - Alertas de cambios críticos
   - Resumen semanal de actividad

4. **Permisos Granulares:**
   - Crear permisos personalizados
   - Asignar permisos individuales
   - Templates de roles

---

## 📞 CONTACTO Y SOPORTE

**Desarrollador:** Jonathan Cerda  
**Email:** jonathan.cerda@agrovetmarket.com  
**Fecha de Implementación:** 21 de abril de 2026  
**Versión:** 1.0.0

---

**FIN DE LA DOCUMENTACIÓN**
