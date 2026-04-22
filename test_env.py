import os
from dotenv import load_dotenv

# Cargar .env
load_dotenv()

# Verificar DATABASE_URL
db_url = os.getenv('DATABASE_URL')

if db_url:
    print(f"✅ DATABASE_URL encontrada: {db_url[:60]}...")
    print(f"   Longitud: {len(db_url)} caracteres")
else:
    print("❌ DATABASE_URL NO ENCONTRADA")

# Verificar otras variables
print(f"\n📋 Otras variables:")
print(f"   ODOO_URL: {os.getenv('ODOO_URL')}")
print(f"   SUPABASE_URL: {os.getenv('SUPABASE_URL')}")
print(f"   SECRET_KEY: {'Configurada' if os.getenv('SECRET_KEY') else 'NO configurada'}")
