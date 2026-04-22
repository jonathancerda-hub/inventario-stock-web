"""
Script de Migración de Datos: Supabase Free → Supabase Pro
=========================================================
Proyecto: Inventario Stock Web
Fecha: 2026-04-01
Autor: Jonathan Cerda

Descripción:
    Este script migra los datos de la tabla page_visits desde el proyecto
    Supabase Free actual al nuevo proyecto Supabase Pro.
    
    Características:
    - Migración en lotes (batch processing)
    - Progreso en tiempo real
    - Manejo de errores robusto
    - Validación de integridad post-migración
    - Actualización automática de secuencias

Uso:
    1. Configurar las URLs en las constantes OLD_DB_URL y NEW_DB_URL
    2. Ejecutar: python migrate_data_to_pro.py
    3. Monitorear el progreso en la consola
    
Nota:
    Este script es OPCIONAL. Solo usarlo si:
    - Hay más de 10,000 filas
    - pg_dump/psql falla por alguna razón
    - Se requiere control fino del proceso
"""

import psycopg2
import psycopg2.extras
from datetime import datetime
import sys
from typing import Optional, Tuple

# ============================================
# CONFIGURACIÓN
# ============================================

# URL del proyecto Supabase Free (ORIGEN)
OLD_DB_URL = "postgresql://postgres.ppmbwujtfueilifisxhs:[PASSWORD]@aws-0-us-west-1.pooler.supabase.com:6543/postgres"

# URL del proyecto Supabase Pro (DESTINO)
NEW_DB_URL = "postgresql://postgres.[NEW_PROJECT_REF]:[NEW_PASSWORD]@aws-0-[NEW_REGION].pooler.supabase.com:6543/postgres"

# Tamaño de lote para inserción (ajustar según RAM disponible)
BATCH_SIZE = 1000

# Modo dry-run (True = no inserta, solo simula)
DRY_RUN = False

# ============================================
# FUNCIONES
# ============================================

def connect_to_db(db_url: str, db_name: str) -> Optional[psycopg2.extensions.connection]:
    """
    Conecta a una base de datos PostgreSQL.
    
    Args:
        db_url: URL de conexión PostgreSQL
        db_name: Nombre descriptivo de la DB (para logs)
    
    Returns:
        Conexión de psycopg2 o None si falla
    """
    try:
        conn = psycopg2.connect(db_url)
        print(f"✅ Conectado a {db_name}")
        return conn
    except Exception as e:
        print(f"❌ Error conectando a {db_name}: {e}")
        return None


def get_row_count(conn: psycopg2.extensions.connection, table: str) -> int:
    """
    Obtiene el número de filas en una tabla.
    
    Args:
        conn: Conexión a la base de datos
        table: Nombre de la tabla
    
    Returns:
        Número de filas
    """
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            return count
    except Exception as e:
        print(f"❌ Error obteniendo count: {e}")
        return 0


def export_data(conn: psycopg2.extensions.connection) -> Optional[list]:
    """
    Exporta todos los datos de page_visits del proyecto antiguo.
    
    Args:
        conn: Conexión al proyecto Supabase Free
    
    Returns:
        Lista de tuplas con los datos o None si falla
    """
    try:
        print("\n📦 Exportando datos del proyecto Free...")
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    id, user_email, user_name, page_url, page_title,
                    visit_timestamp, session_duration, ip_address,
                    user_agent, referrer, method
                FROM page_visits
                ORDER BY id ASC
            """)
            rows = cursor.fetchall()
            print(f"✅ Se exportaron {len(rows)} registros")
            return rows
    except Exception as e:
        print(f"❌ Error exportando datos: {e}")
        return None


def import_data_batch(
    conn: psycopg2.extensions.connection,
    rows: list,
    batch_size: int = 1000,
    dry_run: bool = False
) -> Tuple[int, int]:
    """
    Importa datos en lotes al proyecto nuevo.
    
    Args:
        conn: Conexión al proyecto Supabase Pro
        rows: Lista de tuplas con los datos a importar
        batch_size: Tamaño de cada lote
        dry_run: Si True, solo simula sin insertar
    
    Returns:
        Tupla (registros_exitosos, registros_fallidos)
    """
    total_rows = len(rows)
    success_count = 0
    error_count = 0
    
    print(f"\n📥 Importando {total_rows} registros en lotes de {batch_size}...")
    
    if dry_run:
        print("⚠️  MODO DRY-RUN ACTIVADO - No se insertarán datos reales")
    
    try:
        with conn.cursor() as cursor:
            for i in range(0, total_rows, batch_size):
                batch = rows[i:i + batch_size]
                batch_num = (i // batch_size) + 1
                total_batches = (total_rows + batch_size - 1) // batch_size
                
                try:
                    if not dry_run:
                        # Usar execute_values para inserción eficiente
                        psycopg2.extras.execute_values(
                            cursor,
                            """
                            INSERT INTO page_visits 
                            (id, user_email, user_name, page_url, page_title,
                             visit_timestamp, session_duration, ip_address,
                             user_agent, referrer, method)
                            VALUES %s
                            ON CONFLICT (id) DO NOTHING
                            """,
                            batch,
                            page_size=batch_size
                        )
                        conn.commit()
                    
                    success_count += len(batch)
                    progress = (i + len(batch)) / total_rows * 100
                    print(f"  ✅ Lote {batch_num}/{total_batches} completado - "
                          f"{i + len(batch)}/{total_rows} filas ({progress:.1f}%)")
                
                except Exception as e:
                    error_count += len(batch)
                    print(f"  ❌ Error en lote {batch_num}: {e}")
                    conn.rollback()
                    
                    # Intentar reinsertar fila por fila (más lento pero seguro)
                    print(f"  🔄 Reintentando lote {batch_num} fila por fila...")
                    for row in batch:
                        try:
                            if not dry_run:
                                cursor.execute("""
                                    INSERT INTO page_visits 
                                    (id, user_email, user_name, page_url, page_title,
                                     visit_timestamp, session_duration, ip_address,
                                     user_agent, referrer, method)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                    ON CONFLICT (id) DO NOTHING
                                """, row)
                                conn.commit()
                            success_count += 1
                            error_count -= 1
                        except Exception as row_error:
                            print(f"    ⚠️  Fila con id={row[0]} falló: {row_error}")
    
    except Exception as e:
        print(f"❌ Error crítico durante importación: {e}")
        conn.rollback()
    
    return success_count, error_count


def update_sequence(conn: psycopg2.extensions.connection) -> bool:
    """
    Actualiza la secuencia de id para que continúe correctamente.
    
    Args:
        conn: Conexión al proyecto Supabase Pro
    
    Returns:
        True si se actualizó correctamente, False si falló
    """
    try:
        print("\n🔢 Actualizando secuencia de IDs...")
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT setval('page_visits_id_seq', 
                             (SELECT MAX(id) FROM page_visits));
            """)
            new_seq_value = cursor.fetchone()[0]
            conn.commit()
            print(f"✅ Secuencia actualizada a {new_seq_value}")
            return True
    except Exception as e:
        print(f"❌ Error actualizando secuencia: {e}")
        return False


def validate_migration(
    old_conn: psycopg2.extensions.connection,
    new_conn: psycopg2.extensions.connection
) -> bool:
    """
    Valida que la migración fue exitosa comparando datos.
    
    Args:
        old_conn: Conexión al proyecto Free (origen)
        new_conn: Conexión al proyecto Pro (destino)
    
    Returns:
        True si la validación pasa, False si hay discrepancias
    """
    print("\n🔍 Validando migración...")
    
    try:
        # Comparar counts
        old_count = get_row_count(old_conn, 'page_visits')
        new_count = get_row_count(new_conn, 'page_visits')
        
        print(f"  • Filas en origen (Free): {old_count}")
        print(f"  • Filas en destino (Pro): {new_count}")
        
        if old_count != new_count:
            print(f"  ⚠️  DISCREPANCIA: Faltan {old_count - new_count} filas")
            return False
        
        # Comparar usuarios únicos
        with old_conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(DISTINCT user_email) FROM page_visits")
            old_users = cursor.fetchone()[0]
        
        with new_conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(DISTINCT user_email) FROM page_visits")
            new_users = cursor.fetchone()[0]
        
        print(f"  • Usuarios únicos en origen: {old_users}")
        print(f"  • Usuarios únicos en destino: {new_users}")
        
        if old_users != new_users:
            print(f"  ⚠️  DISCREPANCIA en usuarios únicos")
            return False
        
        # Comparar rangos de fechas
        with old_conn.cursor() as cursor:
            cursor.execute("SELECT MIN(visit_timestamp), MAX(visit_timestamp) FROM page_visits")
            old_min, old_max = cursor.fetchone()
        
        with new_conn.cursor() as cursor:
            cursor.execute("SELECT MIN(visit_timestamp), MAX(visit_timestamp) FROM page_visits")
            new_min, new_max = cursor.fetchone()
        
        print(f"  • Rango de fechas origen: {old_min} → {old_max}")
        print(f"  • Rango de fechas destino: {new_min} → {new_max}")
        
        if old_min != new_min or old_max != new_max:
            print(f"  ⚠️  DISCREPANCIA en rangos de fechas")
            return False
        
        print("  ✅ Validación exitosa - Los datos coinciden")
        return True
    
    except Exception as e:
        print(f"  ❌ Error durante validación: {e}")
        return False


def optimize_new_database(conn: psycopg2.extensions.connection) -> None:
    """
    Ejecuta optimizaciones en la nueva base de datos.
    
    Args:
        conn: Conexión al proyecto Supabase Pro
    """
    print("\n⚡ Optimizando base de datos Pro...")
    
    try:
        with conn.cursor() as cursor:
            # Recopilar estadísticas para el query planner
            print("  • Ejecutando ANALYZE...")
            cursor.execute("ANALYZE page_visits;")
            
            # Reindexar para optimizar índices
            print("  • Reindexando tabla...")
            cursor.execute("REINDEX TABLE page_visits;")
            
            conn.commit()
            print("  ✅ Optimización completada")
    
    except Exception as e:
        print(f"  ⚠️  Error durante optimización: {e}")


# ============================================
# SCRIPT PRINCIPAL
# ============================================

def main():
    """Función principal de migración."""
    print("=" * 60)
    print("MIGRACIÓN DE DATOS: SUPABASE FREE → SUPABASE PRO")
    print("=" * 60)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Batch size: {BATCH_SIZE}")
    print(f"Dry-run: {'Sí' if DRY_RUN else 'No'}")
    print("=" * 60)
    
    # Validar que las URLs estén configuradas
    if "[PASSWORD]" in OLD_DB_URL or "[NEW_PROJECT_REF]" in NEW_DB_URL:
        print("\n❌ ERROR: Las URLs de conexión no están configuradas correctamente")
        print("   → Editar las constantes OLD_DB_URL y NEW_DB_URL en el script")
        sys.exit(1)
    
    # Conectar a ambas bases de datos
    old_conn = connect_to_db(OLD_DB_URL, "Supabase Free (origen)")
    new_conn = connect_to_db(NEW_DB_URL, "Supabase Pro (destino)")
    
    if not old_conn or not new_conn:
        print("\n❌ No se pudo establecer las conexiones necesarias")
        sys.exit(1)
    
    try:
        # Mostrar estadísticas iniciales
        old_count = get_row_count(old_conn, 'page_visits')
        new_count = get_row_count(new_conn, 'page_visits')
        
        print(f"\n📊 Estado inicial:")
        print(f"  • Filas en origen (Free): {old_count}")
        print(f"  • Filas en destino (Pro): {new_count}")
        
        if new_count > 0:
            print(f"\n⚠️  ADVERTENCIA: La tabla de destino ya tiene {new_count} filas")
            response = input("¿Continuar de todas formas? (s/n): ")
            if response.lower() != 's':
                print("Migración cancelada por el usuario")
                sys.exit(0)
        
        # Exportar datos
        rows = export_data(old_conn)
        if not rows:
            print("\n❌ No se pudieron exportar los datos")
            sys.exit(1)
        
        # Importar datos
        success_count, error_count = import_data_batch(
            new_conn, 
            rows, 
            batch_size=BATCH_SIZE,
            dry_run=DRY_RUN
        )
        
        print(f"\n📊 Resultado de importación:")
        print(f"  ✅ Registros exitosos: {success_count}")
        print(f"  ❌ Registros fallidos: {error_count}")
        
        if not DRY_RUN:
            # Actualizar secuencia
            update_sequence(new_conn)
            
            # Validar migración
            is_valid = validate_migration(old_conn, new_conn)
            
            if is_valid:
                # Optimizar base de datos
                optimize_new_database(new_conn)
                
                print("\n" + "=" * 60)
                print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
                print("=" * 60)
                print("\nPróximos pasos:")
                print("1. Verificar datos en Supabase Pro Dashboard")
                print("2. Actualizar DATABASE_URL en .env y Render")
                print("3. Probar la aplicación localmente")
                print("4. Desplegar a producción")
                print("5. Monitorear por 7 días")
                print("6. Backup y eliminar proyecto Free")
            else:
                print("\n⚠️  VALIDACIÓN FALLÓ - Revisar discrepancias antes de continuar")
        else:
            print("\n✅ DRY-RUN COMPLETADO - No se insertaron datos reales")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Migración interrumpida por el usuario")
    
    except Exception as e:
        print(f"\n❌ Error crítico: {e}")
    
    finally:
        # Cerrar conexiones
        if old_conn:
            old_conn.close()
            print("\n🔌 Conexión a Free cerrada")
        if new_conn:
            new_conn.close()
            print("🔌 Conexión a Pro cerrada")


if __name__ == "__main__":
    main()
