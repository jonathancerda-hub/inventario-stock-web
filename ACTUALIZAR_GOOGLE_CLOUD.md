# ✅ ACTUALIZA GOOGLE CLOUD CONSOLE

## IMPORTANTE: Cambia la URI de redirección

El proyecto ahora usa **Authlib** en lugar de google-auth-oauthlib.

### Pasos para actualizar:

1. Ve a: https://console.cloud.google.com/apis/credentials
2. Busca tu OAuth Client ID: `405410518889-j4t96qq2nbjgmrbkkv9kmjnr43p57sl2`
3. En **"Authorized redirect URIs"**, CAMBIA o AGREGA:
   ```
   http://localhost:5000/authorize
   ```
   
4. **ELIMINA** (si existe):
   ```
   http://localhost:5000/auth/callback
   ```

5. Guarda los cambios
6. Espera 2-3 minutos para que se propaguen los cambios
7. Prueba el login en: http://localhost:5000

## Ruta actualizada

- **Antes**: `/auth/callback`
- **Ahora**: `/authorize`

## Flujo de autenticación

1. Usuario hace clic en "Sign in with Google" en `/login`
2. Se redirige a `/google-oauth`
3. Google autentica y redirige a `/authorize`
4. El sistema valida y crea la sesión

¡Listo! Ahora funciona con Authlib como en tu guía.
