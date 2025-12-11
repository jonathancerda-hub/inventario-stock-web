# Script para generar la lista de emails en formato para Render
# Uso: python generate_whitelist_env.py

import os

def generate_env_format():
    whitelist_path = os.path.join(os.path.dirname(__file__), 'whitelist.txt')
    
    if not os.path.exists(whitelist_path):
        print("❌ Error: No se encontró el archivo whitelist.txt")
        return
    
    emails = []
    
    with open(whitelist_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Ignorar líneas vacías y comentarios
            if line and not line.startswith('#'):
                emails.append(line)
    
    if not emails:
        print("❌ No se encontraron emails en whitelist.txt")
        return
    
    # Generar string separado por comas
    env_string = ','.join(emails)
    
    print("=" * 80)
    print("📋 VARIABLE DE ENTORNO PARA RENDER")
    print("=" * 80)
    print("\nNombre de la variable:")
    print("  WHITELIST_EMAILS")
    print("\nValor de la variable (copia esto):")
    print("-" * 80)
    print(env_string)
    print("-" * 80)
    print(f"\n✅ Total de usuarios: {len(emails)}")
    print("\nPasos en Render:")
    print("1. Ve a tu servicio > Environment")
    print("2. Add Environment Variable")
    print("3. Key: WHITELIST_EMAILS")
    print("4. Value: Copia el texto de arriba")
    print("5. Save Changes")
    print("\n" + "=" * 80)

if __name__ == "__main__":
    generate_env_format()
