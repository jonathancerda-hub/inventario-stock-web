"""
Script de Validación Post-Migración
===================================
Verifica la integridad de datos después de migrar a Supabase Pro

Uso:
    python validate_migration.py

O simplemente responder las preguntas del script interactivo.
"""

import psycopg2
from datetime import datetime
import sys

def get_db_stats(conn, project_name):
    """Obtiene estadísticas de la base de datos."""
    print(f"\n📊 Estadísticas de {project_name}:")
    print("-" * 50)
    
    try:
        with conn.cursor() as cursor:
            # Total de filas
            cursor.execute("SELECT COUNT(*) FROM page_visits")
            total = cursor.fetchone()[0]
            print(f"Total de filas: {total:,}")
            
            # Usuarios únicos
            cursor.execute("SELECT COUNT(DISTINCT user_email) FROM page_visits")
            users = cursor.fetchone()[0]
            print(f"Usuarios únicos: {users:,}")
            
            # Rango de fechas
            cursor.execute("""
                SELECT 
                    MIN(visit_timestamp) as primera_visita,
                    MAX(visit_timestamp) as ultima_visita
                FROM page_visits
            """)
            first, last = cursor.fetchone()
            print(f"Primera visita: {first}")
            print(f"Última visita: {last}")
            
            # Top 5 páginas más visitadas
            cursor.execute("""
                SELECT page_url, COUNT(*) as visitas
                FROM page_visits
                GROUP BY page_url
                ORDER BY visitas DESC
                LIMIT 5
            """)
            print("\nTop 5 páginas más visitadas:")
            for url, count in cursor.fetchall():
                print(f"  • {url}: {count:,} visitas")
            
            # Tamaño de la tabla
            cursor.execute("""
                SELECT pg_size_pretty(pg_total_relation_size('page_visits'))
            """)
            size = cursor.fetchone()[0]
            print(f"\nTamaño total (tabla + índices): {size}")
            
            return {
                'total': total,
                'users': users,
                'first_visit': first,
                'last_visit': last,
                'size': size
            }
    
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas: {e}")
        return None


def main():
    print("=" * 60)
    print("VALIDACIÓN DE MIGRACIÓN A SUPABASE PRO")
    print("=" * 60)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Solicitar URLs
    print("Ingresa las URLs de conexión:")
    print("\nProyecto Free (origen):")
    old_url = input("URL: ").strip()
    
    print("\nProyecto Pro (destino):")
    new_url = input("URL: ").strip()
    
    if not old_url or not new_url:
        print("\n❌ Debes proporcionar ambas URLs")
        sys.exit(1)
    
    # Conectar
    print("\n🔌 Conectando a las bases de datos...")
    
    try:
        old_conn = psycopg2.connect(old_url)
        print("✅ Conectado a proyecto Free")
    except Exception as e:
        print(f"❌ Error conectando a Free: {e}")
        sys.exit(1)
    
    try:
        new_conn = psycopg2.connect(new_url)
        print("✅ Conectado a proyecto Pro")
    except Exception as e:
        print(f"❌ Error conectando a Pro: {e}")
        sys.exit(1)
    
    # Obtener estadísticas
    old_stats = get_db_stats(old_conn, "PROYECTO FREE")
    new_stats = get_db_stats(new_conn, "PROYECTO PRO")
    
    if not old_stats or not new_stats:
        print("\n❌ No se pudieron obtener las estadísticas")
        sys.exit(1)
    
    # Comparar
    print("\n" + "=" * 60)
    print("🔍 COMPARACIÓN DE RESULTADOS")
    print("=" * 60)
    
    all_ok = True
    
    # Total de filas
    if old_stats['total'] == new_stats['total']:
        print(f"✅ Total de filas: {old_stats['total']:,} (coincide)")
    else:
        print(f"❌ Total de filas NO coincide:")
        print(f"   Free: {old_stats['total']:,}")
        print(f"   Pro:  {new_stats['total']:,}")
        print(f"   Diferencia: {abs(old_stats['total'] - new_stats['total']):,}")
        all_ok = False
    
    # Usuarios únicos
    if old_stats['users'] == new_stats['users']:
        print(f"✅ Usuarios únicos: {old_stats['users']:,} (coincide)")
    else:
        print(f"❌ Usuarios únicos NO coincide:")
        print(f"   Free: {old_stats['users']:,}")
        print(f"   Pro:  {new_stats['users']:,}")
        all_ok = False
    
    # Fechas
    if (old_stats['first_visit'] == new_stats['first_visit'] and 
        old_stats['last_visit'] == new_stats['last_visit']):
        print(f"✅ Rangos de fechas coinciden")
    else:
        print(f"⚠️  Rangos de fechas NO coinciden completamente:")
        print(f"   Primera visita - Free: {old_stats['first_visit']}")
        print(f"   Primera visita - Pro:  {new_stats['first_visit']}")
        print(f"   Última visita - Free:  {old_stats['last_visit']}")
        print(f"   Última visita - Pro:   {new_stats['last_visit']}")
        all_ok = False
    
    # Resultado final
    print("\n" + "=" * 60)
    if all_ok:
        print("✅ VALIDACIÓN EXITOSA - LOS DATOS COINCIDEN")
        print("=" * 60)
        print("\nLa migración fue exitosa. Puedes proceder con:")
        print("1. Actualizar DATABASE_URL en producción")
        print("2. Desplegar la aplicación")
        print("3. Monitorear por 7 días")
        print("4. Eliminar proyecto Free después")
    else:
        print("⚠️  VALIDACIÓN FALLÓ - HAY DISCREPANCIAS")
        print("=" * 60)
        print("\nRevisiones recomendadas:")
        print("1. Verificar que la migración completó correctamente")
        print("2. Revisar logs del script de migración")
        print("3. Considerar re-ejecutar la migración")
        print("4. NO eliminar proyecto Free hasta resolver")
    
    # Cerrar conexiones
    old_conn.close()
    new_conn.close()
    print("\n🔌 Conexiones cerradas\n")


if __name__ == "__main__":
    main()
