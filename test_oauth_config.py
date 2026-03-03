# Script para verificar configuración OAuth2
from dotenv import load_dotenv
import os

load_dotenv()

print("=" * 60)
print("VERIFICACIÓN DE CONFIGURACIÓN OAUTH2")
print("=" * 60)

client_id = os.getenv('GOOGLE_CLIENT_ID')
client_secret = os.getenv('GOOGLE_CLIENT_SECRET')

print(f"\n✓ GOOGLE_CLIENT_ID encontrado: {'Sí' if client_id else 'NO'}")
if client_id:
    print(f"  Valor: {client_id[:20]}...{client_id[-20:]}")
    print(f"  Longitud: {len(client_id)} caracteres")
    
print(f"\n✓ GOOGLE_CLIENT_SECRET encontrado: {'Sí' if client_secret else 'NO'}")
if client_secret:
    print(f"  Valor: {client_secret[:10]}...{client_secret[-5:]}")
    print(f"  Longitud: {len(client_secret)} caracteres")

print("\n" + "=" * 60)
print("RECOMENDACIONES:")
print("=" * 60)

if not client_id or not client_secret:
    print("❌ Faltan credenciales en el archivo .env")
    print("   Agrega GOOGLE_CLIENT_ID y GOOGLE_CLIENT_SECRET")
elif not client_id.endswith('.apps.googleusercontent.com'):
    print("⚠️  El CLIENT_ID no tiene el formato esperado")
    print("   Debería terminar en '.apps.googleusercontent.com'")
elif not client_secret.startswith('GOCSPX-'):
    print("⚠️  El CLIENT_SECRET no tiene el formato esperado")
    print("   Debería comenzar con 'GOCSPX-'")
else:
    print("✓ Las credenciales parecen tener el formato correcto")
    print("\nSi aún hay error 401:")
    print("1. Verifica las URIs de redirección en Google Cloud Console")
    print("2. Asegúrate de que sean EXACTAMENTE:")
    print("   - http://localhost:5000/auth/callback")
    print("   - http://127.0.0.1:5000/auth/callback")
    print("3. Espera 5-10 minutos para que se propaguen los cambios")
    print("4. Considera crear nuevas credenciales OAuth2")

print("\n")
