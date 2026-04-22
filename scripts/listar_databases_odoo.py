"""
Lista las bases de datos disponibles en el servidor Odoo
"""
import xmlrpc.client
import os
from dotenv import load_dotenv

load_dotenv()

ODOO_URL = os.getenv('ODOO_URL')

print("=" * 60)
print("📋 LISTANDO BASES DE DATOS DISPONIBLES")
print("=" * 60)
print(f"Servidor: {ODOO_URL}")
print()

try:
    db = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/db')
    databases = db.list()
    
    if databases:
        print(f"✅ Bases de datos encontradas ({len(databases)}):")
        print()
        for i, db_name in enumerate(databases, 1):
            print(f"   {i}. {db_name}")
    else:
        print("⚠️  No se encontraron bases de datos accesibles")
        print()
        print("Posibles causas:")
        print("- El servidor tiene deshabilitada la lista pública de DBs")
        print("- No tienes permisos para listar las bases de datos")
        
except Exception as e:
    print(f"❌ Error al listar bases de datos:")
    print(f"   {str(e)}")
    print()
    print("El servidor Odoo puede tener deshabilitada esta función por seguridad")

print()
print("=" * 60)
print("💡 CÓMO OBTENER EL NOMBRE CORRECTO DE LA BASE DE DATOS:")
print("=" * 60)
print()
print("1. Inicia sesión en tu instancia Odoo: {ODOO_URL}")
print("2. Mira la URL después de iniciar sesión")
print("3. El nombre de la BD suele estar en la URL o en 'Configuración > Base de datos'")
print("4. También puedes pedirle el nombre al administrador de Odoo")
