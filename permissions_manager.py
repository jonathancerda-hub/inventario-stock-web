"""
permissions_manager.py - Gestor de Permisos y Usuarios

Sistema centralizado para gestionar usuarios, roles y permisos del sistema.
Implementado con Supabase PostgreSQL.

Fecha: 21 de abril de 2026
Proyecto: Inventario Stock
"""

import os
from typing import Optional, Dict, List, Tuple
from datetime import datetime
import pytz
from dotenv import load_dotenv
from logging_config import get_logger

# Cargar variables de entorno
load_dotenv()

logger = get_logger('permissions_manager')


class PermissionsManager:
    """
    Gestor centralizado de permisos y roles de usuario.
    
    Roles disponibles:
    - admin_full: Acceso completo al sistema (gestión de usuarios, analytics, configuración)
    - dashboard_user: Acceso al dashboard con KPIs y gráficos
    - inventory_user: Solo consulta de inventario básica
    - viewer: Solo visualización (sin exportaciones)
    """
    
    # Definición de roles y permisos
    ROLE_PERMISSIONS = {
        'admin_full': [
            'view_inventory',
            'export_inventory',
            'view_dashboard',
            'export_dashboard',
            'view_analytics',
            'manage_users',
            'view_audit_log',
            'manage_settings'
        ],
        'dashboard_user': [
            'view_inventory',
            'export_inventory',
            'view_dashboard',
            'export_dashboard'
        ],
        'inventory_user': [
            'view_inventory',
            'export_inventory'
        ],
        'viewer': [
            'view_inventory'
        ]
    }
    
    def __init__(self):
        """Inicializa conexión con Supabase"""
        self.database_url = os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL no configurada en variables de entorno")
        
        # Zona horaria de Perú
        self.local_tz = pytz.timezone('America/Lima')
        
        logger.info("PermissionsManager inicializado con Supabase PostgreSQL")
    
    def _get_connection(self):
        """Obtiene conexión a Supabase PostgreSQL"""
        import psycopg2
        return psycopg2.connect(self.database_url)
    
    # ==================== CRUD OPERATIONS ====================
    
    def add_user(self, email: str, role: str, created_by: str = 'admin') -> bool:
        """
        Agrega un nuevo usuario al sistema.
        
        Args:
            email: Email corporativo del usuario
            role: Rol a asignar (debe estar en ROLE_PERMISSIONS)
            created_by: Email del admin que crea el usuario
            
        Returns:
            bool: True si se creó exitosamente, False si ya existe
            
        Raises:
            ValueError: Si el rol no es válido
        """
        if role not in self.ROLE_PERMISSIONS:
            raise ValueError(f"Rol inválido: {role}. Roles válidos: {list(self.ROLE_PERMISSIONS.keys())}")
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO inventario_user_permissions (email, role, created_by, is_active)
                VALUES (%s, %s, %s, TRUE)
                ON CONFLICT (email) DO NOTHING
                RETURNING id
            """, (email.lower(), role, created_by))
            
            result = cursor.fetchone()
            conn.commit()
            
            if result:
                logger.info(f"Usuario creado: {email} con rol {role} por {created_by}")
                return True
            else:
                logger.warning(f"Usuario ya existe: {email}")
                return False
                
        except Exception as e:
            logger.error(f"Error al agregar usuario {email}: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_user_role(self, email: str) -> Optional[str]:
        """
        Obtiene el rol de un usuario.
        
        Args:
            email: Email del usuario
            
        Returns:
            str: Rol del usuario o None si no existe o está inactivo
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT role FROM inventario_user_permissions
                WHERE email = %s AND is_active = TRUE
            """, (email.lower(),))
            
            result = cursor.fetchone()
            return result[0] if result else None
            
        except Exception as e:
            logger.error(f"Error al obtener rol de {email}: {e}")
            return None
        finally:
            cursor.close()
            conn.close()
    
    def update_user_role(self, email: str, new_role: str, updated_by: str = 'admin') -> bool:
        """
        Actualiza el rol de un usuario existente.
        
        Args:
            email: Email del usuario
            new_role: Nuevo rol a asignar
            updated_by: Email del admin que hace el cambio
            
        Returns:
            bool: True si se actualizó, False si no existe
        """
        if new_role not in self.ROLE_PERMISSIONS:
            raise ValueError(f"Rol inválido: {new_role}")
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE inventario_user_permissions
                SET role = %s, updated_at = NOW()
                WHERE email = %s AND is_active = TRUE
                RETURNING id
            """, (new_role, email.lower()))
            
            result = cursor.fetchone()
            conn.commit()
            
            if result:
                logger.info(f"Rol actualizado: {email} -> {new_role} por {updated_by}")
                return True
            else:
                logger.warning(f"Usuario no encontrado o inactivo: {email}")
                return False
                
        except Exception as e:
            logger.error(f"Error al actualizar rol de {email}: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def delete_user(self, email: str, deleted_by: str = 'admin') -> bool:
        """
        Desactiva un usuario (soft delete).
        
        Args:
            email: Email del usuario
            deleted_by: Email del admin que elimina
            
        Returns:
            bool: True si se desactivó, False si no existe
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE inventario_user_permissions
                SET is_active = FALSE, updated_at = NOW()
                WHERE email = %s AND is_active = TRUE
                RETURNING id
            """, (email.lower(),))
            
            result = cursor.fetchone()
            conn.commit()
            
            if result:
                logger.info(f"Usuario desactivado: {email} por {deleted_by}")
                return True
            else:
                logger.warning(f"Usuario no encontrado: {email}")
                return False
                
        except Exception as e:
            logger.error(f"Error al desactivar usuario {email}: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def reactivate_user(self, email: str, reactivated_by: str = 'admin') -> bool:
        """
        Reactiva un usuario desactivado.
        
        Args:
            email: Email del usuario
            reactivated_by: Email del admin que reactiva
            
        Returns:
            bool: True si se reactivó, False si no existe
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE inventario_user_permissions
                SET is_active = TRUE, updated_at = NOW()
                WHERE email = %s AND is_active = FALSE
                RETURNING id
            """, (email.lower(),))
            
            result = cursor.fetchone()
            conn.commit()
            
            if result:
                logger.info(f"Usuario reactivado: {email} por {reactivated_by}")
                return True
            else:
                logger.warning(f"Usuario no encontrado o ya activo: {email}")
                return False
                
        except Exception as e:
            logger.error(f"Error al reactivar usuario {email}: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def list_users(self, role_filter: Optional[str] = None, include_inactive: bool = False) -> List[Dict]:
        """
        Lista todos los usuarios del sistema.
        
        Args:
            role_filter: Filtrar por rol específico
            include_inactive: Incluir usuarios desactivados
            
        Returns:
            List[Dict]: Lista de usuarios con sus datos
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT 
                    email, role, is_active, created_at, updated_at,
                    created_by, last_login
                FROM inventario_user_permissions
                WHERE 1=1
            """
            params = []
            
            if not include_inactive:
                query += " AND is_active = TRUE"
            
            if role_filter:
                query += " AND role = %s"
                params.append(role_filter)
            
            query += " ORDER BY created_at DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            users = []
            for row in rows:
                users.append({
                    'email': row[0],
                    'role': row[1],
                    'is_active': row[2],
                    'created_at': row[3].strftime('%Y-%m-%d %H:%M:%S') if row[3] else None,
                    'updated_at': row[4].strftime('%Y-%m-%d %H:%M:%S') if row[4] else None,
                    'created_by': row[5],
                    'last_login': row[6].strftime('%Y-%m-%d %H:%M:%S') if row[6] else None,
                    'permissions': self.ROLE_PERMISSIONS.get(row[1], [])
                })
            
            return users
            
        except Exception as e:
            logger.error(f"Error al listar usuarios: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
    
    def get_user_details(self, email: str) -> Optional[Dict]:
        """
        Obtiene detalles completos de un usuario.
        
        Args:
            email: Email del usuario
            
        Returns:
            Dict: Datos del usuario o None si no existe
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    email, role, is_active, created_at, updated_at,
                    created_by, last_login
                FROM inventario_user_permissions
                WHERE email = %s
            """, (email.lower(),))
            
            row = cursor.fetchone()
            
            if row:
                return {
                    'email': row[0],
                    'role': row[1],
                    'is_active': row[2],
                    'created_at': row[3].strftime('%Y-%m-%d %H:%M:%S') if row[3] else None,
                    'updated_at': row[4].strftime('%Y-%m-%d %H:%M:%S') if row[4] else None,
                    'created_by': row[5],
                    'last_login': row[6].strftime('%Y-%m-%d %H:%M:%S') if row[6] else None,
                    'permissions': self.ROLE_PERMISSIONS.get(row[1], [])
                }
            return None
            
        except Exception as e:
            logger.error(f"Error al obtener detalles de {email}: {e}")
            return None
        finally:
            cursor.close()
            conn.close()
    
    def user_has_permission(self, email: str, permission: str) -> bool:
        """
        Verifica si un usuario tiene un permiso específico.
        
        Args:
            email: Email del usuario
            permission: Permiso a verificar (ej: 'view_dashboard')
            
        Returns:
            bool: True si tiene el permiso
        """
        role = self.get_user_role(email)
        if not role:
            return False
        
        permissions = self.ROLE_PERMISSIONS.get(role, [])
        return permission in permissions
    
    def update_last_login(self, email: str) -> None:
        """Actualiza la última fecha de login de un usuario"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE inventario_user_permissions
                SET last_login = NOW()
                WHERE email = %s AND is_active = TRUE
            """, (email.lower(),))
            
            conn.commit()
            
        except Exception as e:
            logger.error(f"Error al actualizar last_login de {email}: {e}")
        finally:
            cursor.close()
            conn.close()
    
    def get_stats(self) -> Dict:
        """Obtiene estadísticas del sistema de permisos"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Total de usuarios activos
            cursor.execute("SELECT COUNT(*) FROM inventario_user_permissions WHERE is_active = TRUE")
            total_active = cursor.fetchone()[0]
            
            # Total de usuarios inactivos
            cursor.execute("SELECT COUNT(*) FROM inventario_user_permissions WHERE is_active = FALSE")
            total_inactive = cursor.fetchone()[0]
            
            # Por rol
            cursor.execute("""
                SELECT role, COUNT(*) 
                FROM inventario_user_permissions 
                WHERE is_active = TRUE
                GROUP BY role
            """)
            by_role = dict(cursor.fetchall())
            
            return {
                'total_active': total_active,
                'total_inactive': total_inactive,
                'total': total_active + total_inactive,
                'by_role': by_role
            }
            
        except Exception as e:
            logger.error(f"Error al obtener estadísticas: {e}")
            return {}
        finally:
            cursor.close()
            conn.close()


# Instancia global
permissions_manager = PermissionsManager()
