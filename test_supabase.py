#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba de conexión a Supabase PostgreSQL
Verifica que la tabla de analytics esté configurada correctamente
"""

import os
import sys
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def test_supabase_connection():
    """Prueba la conexión a Supabase y verifica la tabla de analytics"""
    
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ Error: Variable DATABASE_URL no encontrada")
        print("\n💡 Configura DATABASE_URL en tu archivo .env con:")
        print("   DATABASE_URL=postgresql://postgres.ppmbwujtfueilifisxhs:[PASSWORD]@aws-0-us-west-1.pooler.supabase.com:6543/postgres")
        print("\n📖 Ver SUPABASE_SETUP.md para más detalles")
        return False
    
    try:
        print("🔄 Conectando a Supabase PostgreSQL...")
        
        # Conectar a la base de datos
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("✅ Conexión exitosa!\n")
        
        # Verificar que la tabla page_visits existe
        print("🔍 Verificando tabla page_visits...")
        cursor.execute("""
            SELECT table_name, column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'page_visits' 
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        
        if not columns:
            print("❌ Error: Tabla page_visits no encontrada")
            print("\n💡 Ejecuta la migración en Supabase:")
            print("   Ver SUPABASE_SETUP.md para crear la tabla")
            return False
        
        print(f"✅ Tabla encontrada con {len(columns)} columnas:\n")
        for col in columns:
            print(f"   - {col['column_name']: <20} {col['data_type']}")
        
        # Verificar índices
        print("\n🔍 Verificando índices...")
        cursor.execute("""
            SELECT indexname 
            FROM pg_indexes 
            WHERE tablename = 'page_visits';
        """)
        
        indexes = cursor.fetchall()
        print(f"✅ {len(indexes)} índices encontrados:")
        for idx in indexes:
            print(f"   - {idx['indexname']}")
        
        # Contar registros existentes
        print("\n📊 Contando registros existentes...")
        cursor.execute("SELECT COUNT(*) as count FROM page_visits;")
        result = cursor.fetchone()
        count = result['count']
        print(f"📈 Total de visitas registradas: {count}")
        
        # Insertar registro de prueba
        print("\n🧪 Insertando registro de prueba...")
        test_data = {
            'user_email': 'test@test.com',
            'user_name': 'Test User',
            'page_url': '/test',
            'page_title': 'Test Page',
            'visit_timestamp': datetime.now(),
            'ip_address': '127.0.0.1',
            'user_agent': 'Test Script',
            'referrer': None,
            'method': 'GET'
        }
        
        cursor.execute("""
            INSERT INTO page_visits 
            (user_email, user_name, page_url, page_title, visit_timestamp, 
             ip_address, user_agent, referrer, method)
            VALUES (%(user_email)s, %(user_name)s, %(page_url)s, %(page_title)s, 
                    %(visit_timestamp)s, %(ip_address)s, %(user_agent)s, 
                    %(referrer)s, %(method)s)
            RETURNING id;
        """, test_data)
        
        result = cursor.fetchone()
        test_id = result['id']
        conn.commit()
        
        print(f"✅ Registro insertado con ID: {test_id}")
        
        # Leer el registro insertado
        print("\n🔍 Verificando lectura...")
        cursor.execute("""
            SELECT * FROM page_visits 
            WHERE id = %s;
        """, (test_id,))
        
        record = cursor.fetchone()
        print(f"✅ Registro leído correctamente:")
        print(f"   - Email: {record['user_email']}")
        print(f"   - Página: {record['page_url']}")
        print(f"   - Timestamp: {record['visit_timestamp']}")
        
        # Eliminar registro de prueba
        print("\n🧹 Limpiando registro de prueba...")
        cursor.execute("DELETE FROM page_visits WHERE id = %s;", (test_id,))
        conn.commit()
        print("✅ Registro de prueba eliminado")
        
        # Cerrar conexión
        cursor.close()
        conn.close()
        
        print("\n" + "="*60)
        print("🎉 ¡PRUEBA EXITOSA! Supabase configurado correctamente")
        print("="*60)
        print("\n📝 Próximos pasos:")
        print("   1. Configura DATABASE_URL en Render Environment")
        print("   2. Haz deploy de la aplicación")
        print("   3. Verifica logs para confirmar conexión")
        print("\n📖 Más info: SUPABASE_SETUP.md")
        
        return True
        
    except psycopg2.Error as e:
        print(f"\n❌ Error de PostgreSQL: {e}")
        print("\n💡 Posibles causas:")
        print("   - Contraseña incorrecta en DATABASE_URL")
        print("   - URL de conexión mal formateada")
        print("   - Firewall bloqueando conexión")
        print("   - Base de datos Supabase no accesible")
        return False
        
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("  PRUEBA DE CONEXIÓN - SUPABASE POSTGRESQL ANALYTICS")
    print("="*60)
    print()
    
    success = test_supabase_connection()
    
    sys.exit(0 if success else 1)
