"""
audit_logger.py - Sistema de Auditoría de Cambios

Registra todas las operaciones CRUD sobre usuarios y permisos.
Implementado con Supabase PostgreSQL.

Fecha: 21 de abril de 2026
Proyecto: Inventario Stock
"""

import os
import json
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv
from logging_config import get_logger

# Cargar variables de entorno
load_dotenv()

logger = get_logger('audit_logger')


class AuditLogger:
    """
    Sistema de auditoría para registrar cambios en permisos y usuarios.
    
    Tipos de acciones registradas:
    - user_created: Nuevo usuario agregado
    - user_updated: Rol de usuario modificado
    - user_deleted: Usuario desactivado
    - user_reactivated: Usuario reactivado
    - role_changed: Cambio de rol
    - login: Inicio de sesión de usuario
    """
    
    def __init__(self):
        """Inicializa conexión con Supabase"""
        self.database_url = os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL no configurada")
        
        # Zona horaria de Perú
        self.local_tz = pytz.timezone('America/Lima')
        
        logger.info("AuditLogger inicializado con Supabase PostgreSQL")
    
    def _get_connection(self):
        """Obtiene conexión a Supabase PostgreSQL"""
        import psycopg2
        return psycopg2.connect(self.database_url)
    
    def log_action(
        self,
        action: str,
        user_email: str,
        performed_by: str,
        details: Optional[Dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> bool:
        """
        Registra una acción en el log de auditoría.
        
        Args:
            action: Tipo de acción (user_created, user_updated, etc.)
            user_email: Email del usuario afectado
            performed_by: Email del admin que realizó la acción
            details: Diccionario con detalles adicionales
            ip_address: IP desde donde se realizó la acción
            user_agent: User agent del navegador
            
        Returns:
            bool: True si se registró exitosamente
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Convertir details a JSON
            details_json = json.dumps(details) if details else None
            
            cursor.execute("""
                INSERT INTO inventario_audit_log 
                (action, user_email, performed_by, details, ip_address, user_agent)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (action, user_email.lower(), performed_by.lower(), details_json, ip_address, user_agent))
            
            conn.commit()
            
            logger.info(f"Audit log: {action} - {user_email} por {performed_by}")
            return True
            
        except Exception as e:
            logger.error(f"Error al registrar audit log: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    
    def log_user_created(
        self,
        user_email: str,
        role: str,
        created_by: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> bool:
        """Registra creación de usuario"""
        return self.log_action(
            action='user_created',
            user_email=user_email,
            performed_by=created_by,
            details={
                'role': role,
                'timestamp': datetime.now(self.local_tz).isoformat()
            },
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    def log_user_updated(
        self,
        user_email: str,
        old_role: str,
        new_role: str,
        updated_by: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> bool:
        """Registra actualización de rol"""
        return self.log_action(
            action='role_changed',
            user_email=user_email,
            performed_by=updated_by,
            details={
                'old_role': old_role,
                'new_role': new_role,
                'timestamp': datetime.now(self.local_tz).isoformat()
            },
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    def log_user_deleted(
        self,
        user_email: str,
        role: str,
        deleted_by: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> bool:
        """Registra desactivación de usuario"""
        return self.log_action(
            action='user_deleted',
            user_email=user_email,
            performed_by=deleted_by,
            details={
                'role_before_deletion': role,
                'timestamp': datetime.now(self.local_tz).isoformat()
            },
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    def log_user_reactivated(
        self,
        user_email: str,
        role: str,
        reactivated_by: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> bool:
        """Registra reactivación de usuario"""
        return self.log_action(
            action='user_reactivated',
            user_email=user_email,
            performed_by=reactivated_by,
            details={
                'role': role,
                'timestamp': datetime.now(self.local_tz).isoformat()
            },
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    def log_login(
        self,
        user_email: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> bool:
        """Registra inicio de sesión"""
        return self.log_action(
            action='login',
            user_email=user_email,
            performed_by=user_email,
            details={
                'timestamp': datetime.now(self.local_tz).isoformat()
            },
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    def get_logs(
        self,
        limit: int = 100,
        action_filter: Optional[str] = None,
        user_email_filter: Optional[str] = None,
        days_back: int = 30
    ) -> List[Dict]:
        """
        Obtiene logs de auditoría con filtros.
        
        Args:
            limit: Número máximo de registros
            action_filter: Filtrar por tipo de acción
            user_email_filter: Filtrar por email de usuario
            days_back: Días hacia atrás a consultar
            
        Returns:
            List[Dict]: Lista de logs
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT 
                    id, action, user_email, performed_by, details,
                    ip_address, user_agent, timestamp
                FROM inventario_audit_log
                WHERE timestamp >= NOW() - INTERVAL '%s days'
            """
            params = [days_back]
            
            if action_filter:
                query += " AND action = %s"
                params.append(action_filter)
            
            if user_email_filter:
                query += " AND user_email ILIKE %s"
                params.append(f"%{user_email_filter.lower().strip()}%")
            
            query += " ORDER BY timestamp DESC LIMIT %s"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            logs = []
            for row in rows:
                logs.append({
                    'id': row[0],
                    'action': row[1],
                    'user_email': row[2],
                    'performed_by': row[3],
                    'details': json.loads(row[4]) if row[4] else {},
                    'ip_address': row[5],
                    'user_agent': row[6],
                    'timestamp': row[7].strftime('%Y-%m-%d %H:%M:%S') if row[7] else None
                })
            
            return logs
            
        except Exception as e:
            logger.error(f"Error al obtener logs: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
    
    def get_user_history(self, user_email: str, limit: int = 50) -> List[Dict]:
        """
        Obtiene historial completo de un usuario específico.
        
        Args:
            user_email: Email del usuario
            limit: Número máximo de registros
            
        Returns:
            List[Dict]: Historial del usuario
        """
        return self.get_logs(
            limit=limit,
            user_email_filter=user_email,
            days_back=365  # Último año
        )
    
    def get_stats(self, days_back: int = 7) -> Dict:
        """
        Obtiene estadísticas de auditoría.
        
        Args:
            days_back: Días hacia atrás a analizar
            
        Returns:
            Dict: Estadísticas de actividad
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Total de acciones
            cursor.execute("""
                SELECT COUNT(*) 
                FROM inventario_audit_log
                WHERE timestamp >= NOW() - INTERVAL '%s days'
            """, (days_back,))
            total_actions = cursor.fetchone()[0]
            
            # Por tipo de acción
            cursor.execute("""
                SELECT action, COUNT(*)
                FROM inventario_audit_log
                WHERE timestamp >= NOW() - INTERVAL '%s days'
                GROUP BY action
                ORDER BY COUNT(*) DESC
            """, (days_back,))
            by_action = dict(cursor.fetchall())
            
            # Usuarios más activos (quienes realizan cambios)
            cursor.execute("""
                SELECT performed_by, COUNT(*)
                FROM inventario_audit_log
                WHERE timestamp >= NOW() - INTERVAL '%s days'
                    AND action != 'login'
                GROUP BY performed_by
                ORDER BY COUNT(*) DESC
                LIMIT 5
            """, (days_back,))
            most_active_admins = cursor.fetchall()
            
            # Usuarios más modificados
            cursor.execute("""
                SELECT user_email, COUNT(*)
                FROM inventario_audit_log
                WHERE timestamp >= NOW() - INTERVAL '%s days'
                    AND action IN ('user_created', 'role_changed', 'user_deleted', 'user_reactivated')
                GROUP BY user_email
                ORDER BY COUNT(*) DESC
                LIMIT 5
            """, (days_back,))
            most_modified_users = cursor.fetchall()
            
            return {
                'total_actions': total_actions,
                'by_action': by_action,
                'most_active_admins': [{'email': row[0], 'actions': row[1]} for row in most_active_admins],
                'most_modified_users': [{'email': row[0], 'changes': row[1]} for row in most_modified_users],
                'period_days': days_back
            }
            
        except Exception as e:
            logger.error(f"Error al obtener estadísticas de audit: {e}")
            return {}
        finally:
            cursor.close()
            conn.close()


# Instancia global
audit_logger = AuditLogger()
