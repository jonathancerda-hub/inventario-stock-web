"""
Script de diagnóstico para conexión con Odoo
"""
import xmlrpc.client
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración
ODOO_URL = os.getenv('ODOO_URL')
ODOO_DB = os.getenv('ODOO_DB')
ODOO_USER = os.getenv('ODOO_USER')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD')

print("=" * 60)
print("🔍 DIAGNÓSTICO DE CONEXIÓN ODOO")
print("=" * 60)
print()
print(f"URL:      {ODOO_URL}")
print(f"Database: {ODOO_DB}")
print(f"Usuario:  {ODOO_USER}")
print(f"Password: {'*' * len(ODOO_PASSWORD) if ODOO_PASSWORD else 'NO CONFIGURADA'}")
print()

# Test 1: Conectar al endpoint común
print("📡 Test 1: Verificando endpoint /xmlrpc/2/common...")
try:
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    version = common.version()
    print(f"✅ Endpoint común disponible")
    print(f"   Versión Odoo: {version.get('server_version', 'N/A')}")
    print(f"   Serie: {version.get('server_serie', 'N/A')}")
except Exception as e:
    print(f"❌ Error al conectar al endpoint común:")
    print(f"   {str(e)}")
    exit(1)

print()

# Test 2: Autenticación
print("🔐 Test 2: Autenticando usuario...")
try:
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
    if uid:
        print(f"✅ Autenticación exitosa")
        print(f"   User ID: {uid}")
    else:
        print(f"❌ Autenticación fallida")
        print(f"   Posibles causas:")
        print(f"   - Nombre de base de datos incorrecto: '{ODOO_DB}'")
        print(f"   - Usuario o contraseña incorrectos")
        print(f"   - Usuario no tiene acceso a la base de datos")
        exit(1)
except xmlrpc.client.Fault as e:
    print(f"❌ Error XML-RPC durante autenticación:")
    print(f"   Código: {e.faultCode}")
    print(f"   Mensaje: {e.faultString[:200]}")
    
    if "database" in e.faultString.lower():
        print()
        print("💡 SOLUCIÓN: La base de datos no existe o el nombre es incorrecto")
        print(f"   Verifica que '{ODOO_DB}' sea el nombre correcto en Odoo")
    elif "password" in e.faultString.lower() or "authentication" in e.faultString.lower():
        print()
        print("💡 SOLUCIÓN: Credenciales incorrectas")
        print(f"   1. Verifica el usuario: {ODOO_USER}")
        print(f"   2. Genera una nueva API key en Odoo:")
        print(f"      - Mi Cuenta > Preferencias > Seguridad > API Key")
    
    exit(1)
except Exception as e:
    print(f"❌ Error inesperado durante autenticación:")
    print(f"   {str(e)}")
    exit(1)

print()

# Test 3: Acceso a modelos
print("📦 Test 3: Verificando acceso a modelo stock.quant...")
try:
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
    
    # Intentar contar registros
    count = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'stock.quant', 'search_count', [[]]
    )
    
    print(f"✅ Acceso al modelo stock.quant exitoso")
    print(f"   Total de registros: {count}")
    
    if count == 0:
        print()
        print("⚠️  ADVERTENCIA: No hay registros en stock.quant")
        print("   Esto es normal si el inventario está vacío")
    
except Exception as e:
    print(f"❌ Error al acceder a stock.quant:")
    print(f"   {str(e)}")
    print()
    print("💡 SOLUCIÓN: El usuario no tiene permisos para acceder a stock.quant")
    print("   Verifica que el usuario tenga rol de 'Inventario / Usuario'")
    exit(1)

print()

# Test 4: Lectura de datos reales
print("📊 Test 4: Leyendo productos de ejemplo...")
try:
    products = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'stock.quant', 'search_read',
        [[]],
        {'fields': ['product_id', 'location_id', 'quantity'], 'limit': 3}
    )
    
    if products:
        print(f"✅ Lectura de datos exitosa ({len(products)} registros)")
        for i, prod in enumerate(products, 1):
            print(f"   {i}. Producto: {prod.get('product_id', ['N/A'])[1] if isinstance(prod.get('product_id'), list) else 'N/A'}")
            print(f"      Ubicación: {prod.get('location_id', ['N/A'])[1] if isinstance(prod.get('location_id'), list) else 'N/A'}")
            print(f"      Cantidad: {prod.get('quantity', 0)}")
    else:
        print(f"⚠️  No se encontraron productos en stock.quant")
        print("   Esto es normal si el inventario está vacío")
        
except Exception as e:
    print(f"❌ Error al leer datos:")
    print(f"   {str(e)}")
    exit(1)

print()
print("=" * 60)
print("✅ DIAGNÓSTICO COMPLETADO EXITOSAMENTE")
print("=" * 60)
print()
print("🎉 La conexión con Odoo está funcionando correctamente")
print("   Si el problema persiste en la app, revisa:")
print("   - Que el archivo .env esté en la raíz del proyecto")
print("   - Que hayas reiniciado la app después de cambiar .env")
print("   - Los logs de la app para errores específicos")
