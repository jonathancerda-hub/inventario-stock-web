# Solución Error 401: invalid_client

## Opción 1: Descargar credenciales existentes (RECOMENDADO)

1. En Google Cloud Console, en la página de tu OAuth Client ID
2. Busca el botón de **descarga** (icono de flecha hacia abajo) 
3. Descarga el archivo `client_secret_XXXXX.json`
4. Abre el archivo y busca:
   ```json
   {
     "web": {
       "client_id": "......apps.googleusercontent.com",
       "client_secret": "GOCSPX-......"
     }
   }
   ```
5. Copia esos valores EXACTOS al archivo `.env`:
   ```
   GOOGLE_CLIENT_ID=EL_CLIENT_ID_DEL_JSON
   GOOGLE_CLIENT_SECRET=EL_CLIENT_SECRET_DEL_JSON
   ```

## Opción 2: Crear NUEVO OAuth Client ID

1. Ve a: https://console.cloud.google.com/apis/credentials
2. Click en **+ CREATE CREDENTIALS** → **OAuth client ID**
3. Application type: **Web application**
4. Name: `Stock Odoo - Nuevo`
5. Authorized redirect URIs:
   ```
   http://localhost:5000/auth/callback
   http://127.0.0.1:5000/auth/callback
   ```
6. Click **CREATE**
7. COPIA las credenciales que aparecen en el popup
8. Actualiza el archivo `.env` con las NUEVAS credenciales

## Opción 3: Esperar propagación

Si acabas de configurar las URIs, espera **10-15 minutos** antes de volver a intentar.

## Después de actualizar las credenciales:

1. Guarda el archivo `.env`
2. Cierra completamente el navegador
3. Reinicia el servidor Flask
4. Prueba de nuevo el login
