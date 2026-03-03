# Configurar OAuth2 de Google - Paso a Paso

## 1. Ir a Google Cloud Console
Ve a: https://console.cloud.google.com/

## 2. Crear o Seleccionar Proyecto
- Si no tienes un proyecto, crea uno nuevo
- Dale un nombre como "Stock Odoo" o "Inventario Agrovet"

## 3. Habilitar APIs necesarias
Ve a: **APIs & Services** → **Library**
Busca y habilita:
- Google+ API (o People API)
- Google Identity API

## 4. Configurar Pantalla de Consentimiento OAuth
Ve a: **APIs & Services** → **OAuth consent screen**

1. Selecciona **Internal** (para uso solo dentro de tu organización @agrovetmarket.com)
2. Completa la información:
   - App name: `Stock Odoo`
   - User support email: tu email
   - Developer contact: tu email
3. Guarda y continúa

## 5. Crear Credenciales OAuth 2.0
Ve a: **APIs & Services** → **Credentials** → **+ CREATE CREDENTIALS** → **OAuth client ID**

1. Application type: **Web application**
2. Name: `Stock Odoo Web Client`
3. Authorized redirect URIs - Agrega AMBAS:
   ```
   http://localhost:5000/auth/callback
   http://127.0.0.1:5000/auth/callback
   ```
4. Haz clic en **CREATE**

## 6. Copiar Credenciales
Cuando se creen las credenciales, verás un popup con:
- **Client ID** (algo como: XXXXX.apps.googleusercontent.com)
- **Client Secret** (algo como: GOCSPX-XXXXX)

**Copia estos valores y actualiza tu archivo .env**

## 7. Actualizar archivo .env
```env
GOOGLE_CLIENT_ID=TU_NUEVO_CLIENT_ID_AQUI
GOOGLE_CLIENT_SECRET=TU_NUEVO_CLIENT_SECRET_AQUI
```

## 8. Reiniciar la aplicación
Reinicia el servidor Flask para que cargue las nuevas credenciales.

## Nota Importante
- Si tu organización usa Google Workspace, pide a un administrador que apruebe la aplicación
- Las credenciales deben ser de tipo "Web application", NO "Desktop application"
