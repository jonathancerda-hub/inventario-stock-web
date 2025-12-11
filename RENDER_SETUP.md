# Configuración de Whitelist en Render

## Paso 1: Preparar la lista de correos

La lista de correos debe configurarse como una variable de entorno en Render con el nombre `WHITELIST_EMAILS`.

### Formato requerido:
- Emails separados por comas (sin espacios después de la coma, o con espacios que serán eliminados automáticamente)
- Sin comentarios ni líneas vacías
- Ejemplo: `user1@example.com,user2@example.com,user3@example.com`

### Lista actual de correos para copiar en Render:

```
juancarlos.campos@agrovetmarket.com,katherine.navarro@agrovetmarket.com,regina.martinez@agrovetmarket.com,johanna.hurtado@agrovetmarket.com,juan.portal@agrovetmarket.com,manuel.bravo@agrovetmarket.com,sandra.meneses@agrovetmarket.com,stephanie.hiyagon@agrovetmarket.com,carolina.tasayco@agrovetmarket.com,luis.chavez@agrovetmarket.com,thalia.grillo@agrovetmarket.com,jose.delgado@agrovetmarket.com,karina.guillen@agrovetmarket.com,dagoberto.salazar@agrovetmarket.com,samire.huaman@agrovetmarket.com,carmen.morales@agrovetmarket.com,vanessa.parker@agrovetmarket.com,miguel.hernandez@agrovetmarket.com,stefanny.rios@agrovetmarket.com,maria.angulo@agrovetmarket.com,flavia.mendoza@agrovetmarket.com,ariana.carmona@agrovetmarket.com,julian.larosa@agrovetmarket.com,jonathan.reyes@agrovetmarket.com,omar.chavez@agrovetmarket.com,ena.fernandez@agrovetmarket.com,lelia.sanchez@agrovetmarket.com,sandra.krklec@agrovetmarket.com,orlando.jaimes@agrovetmarket.com,jimena.delrisco@agrovetmarket.com,cusi.flores@agrovetmarket.com,janet.hueza@agrovetmarket.com,perci.mondragon@agrovetmarket.com
```

## Paso 2: Configurar en Render

1. Ve a tu servicio en Render Dashboard
2. Click en **"Environment"** en el menú lateral
3. Click en **"Add Environment Variable"**
4. Agrega la variable:
   - **Key**: `WHITELIST_EMAILS`
   - **Value**: Copia la lista de arriba (todos los emails en una sola línea separados por comas)
5. Click en **"Save Changes"**
6. Render reiniciará automáticamente tu servicio

## Paso 3: Verificar otras variables de entorno

Asegúrate de que también tengas configuradas estas variables en Render:

- `ODOO_URL` - URL de tu instancia Odoo
- `ODOO_DB` - Nombre de la base de datos
- `ODOO_USER` - Usuario de Odoo para la conexión
- `ODOO_PASSWORD` - Contraseña del usuario de Odoo

## Funcionamiento

El sistema ahora funciona con **prioridad doble**:

1. **Producción (Render)**: Lee la variable de entorno `WHITELIST_EMAILS`
2. **Desarrollo local**: Si no existe la variable de entorno, lee el archivo `whitelist.txt`

Esto permite:
- ✅ Mantener `whitelist.txt` git-ignored para seguridad
- ✅ Usar variables de entorno en Render (mejor práctica)
- ✅ Desarrollo local sin necesidad de configurar variables de entorno
- ✅ Fácil actualización de usuarios sin redesplegar

## Actualizar la lista de usuarios

### En Render:
1. Ve a Environment variables
2. Edita `WHITELIST_EMAILS`
3. Actualiza la lista de correos
4. Save changes (Render reiniciará automáticamente)

### En desarrollo local:
1. Edita el archivo `whitelist.txt`
2. Reinicia la aplicación Flask

## Logs para verificar

Cuando la aplicación inicie, verás en los logs:
- `✅ Lista blanca cargada desde variable de entorno: X usuarios autorizados` (Render)
- `✅ Lista blanca cargada desde archivo: X usuarios autorizados` (Local)

Si no hay whitelist configurada:
- `⚠️ Advertencia: No se encontró whitelist.txt ni WHITELIST_EMAILS...`

## Seguridad

- ⚠️ **Nunca** commitees el archivo `whitelist.txt` al repositorio (ya está en `.gitignore`)
- ⚠️ **Nunca** expongas la variable `WHITELIST_EMAILS` públicamente
- ✅ Las variables de entorno en Render son seguras y encriptadas
- ✅ Los emails se convierten a minúsculas automáticamente (case-insensitive)
