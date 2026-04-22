# Guías de Codificación Segura — Inventario Stock

**Versión:** 1.0  
**Fecha:** 2026-03-25  
**Aplicación:** `inventario-stock` (Flask + Odoo + PostgreSQL)  
**Estándar Base:** OWASP Top 10 (2021), CWE Top 25, ISO 27001 A.14.2  
**Estado:** ✅ VIGENTE

---

## 1. Propósito y Alcance

Este documento establece las reglas obligatorias de codificación segura para el proyecto **inventario-stock**. Todo colaborador que escriba, revise o apruebe código en este repositorio debe cumplir con estas directrices.

El incumplimiento de las reglas marcadas como **[OBLIGATORIO]** bloquea el merge de un PR.

---

## 2. Gestión de Secretos y Credenciales

### 2.1 Variables de entorno [OBLIGATORIO]

```python
# ✅ CORRECTO — leer desde entorno
SECRET_KEY = os.environ["SECRET_KEY"]           # falla en startup si falta
DATABASE_URL = os.environ.get("DATABASE_URL")   # opcional

# ❌ PROHIBIDO — credenciales hardcodeadas
SECRET_KEY = "mi-clave-super-secreta-2024"
password = "admin123"
```

### 2.2 Archivos prohibidos en git [OBLIGATORIO]

El `.gitignore` **debe incluir** siempre:

```
.env
*.env
whitelist.txt
*credentials*.json
*service_account*.json
odoo_config.py
```

### 2.3 SECRET_KEY [OBLIGATORIO]

- Longitud mínima: **32 bytes** generados con `secrets.token_hex(32)`
- Rotación: **cada 90 días** como mínimo
- Nunca imprimir ni logear el valor de `SECRET_KEY`

---

## 3. Validación y Sanitización de Entradas (A03:2021 — Injection)

### 3.1 Validar toda entrada con Pydantic [OBLIGATORIO cuando se implementa]

```python
# ✅ CORRECTO — Pydantic schema, fronteras del sistema
from schemas import InventoryFilters
from pydantic import ValidationError

@app.route("/inventory", methods=["POST"])
def inventory():
    try:
        filtros = InventoryFilters(**request.form.to_dict())
    except ValidationError as e:
        abort(400)
```

### 3.2 Límites de longitud en strings [OBLIGATORIO]

| Campo | Longitud máxima |
|-------|----------------|
| search_term | 100 caracteres |
| Cualquier ID | int (no string) |
| Nombres | 200 caracteres |

### 3.3 Consultas parametrizadas [OBLIGATORIO]

```python
# ✅ CORRECTO — parámetros separados del SQL
cursor.execute("SELECT * FROM users WHERE email = %s", (email,))

# ❌ PROHIBIDO — concatenación de strings en SQL
cursor.execute(f"SELECT * FROM users WHERE email = '{email}'")
cursor.execute("SELECT * FROM users WHERE email = '" + email + "'")
```

### 3.4 Jinja2 — no deshabilitar autoescape [OBLIGATORIO]

```html
{# ✅ CORRECTO — Jinja2 escapa por defecto #}
<p>{{ user_input }}</p>

{# ❌ PROHIBIDO — rompe XSS protection #}
<p>{{ user_input | safe }}</p>
```

Si un campo debe renderizar HTML (casos excepcionales): documentar la justificación en el PR, sanitizar con `bleach.clean()` antes.

---

## 4. Autenticación y Sesiones (A07:2021 — Auth Failures)

### 4.1 Sesiones Flask [OBLIGATORIO]

```python
# ✅ Configuración mínima requerida
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,   # no accesible desde JS
    SESSION_COOKIE_SAMESITE="Lax",  # mitiga CSRF
    SESSION_COOKIE_SECURE=True,     # solo HTTPS en producción
    PERMANENT_SESSION_LIFETIME=timedelta(minutes=15),
)
```

### 4.2 Protecciones anti-hijacking [OBLIGATORIO]

- Validar `User-Agent` + `IP` en cada request autenticado (fingerprint de sesión)
- Tiempo de inactividad: máximo **15 minutos**
- Al logout: `session.clear()` completo, nunca eliminar solo algunas claves

### 4.3 OAuth / Google [OBLIGATORIO]

- Usar siempre `state` parameter (anti-CSRF en OAuth flow)
- Verificar `hd` (hosted domain) si el acceso es corporativo
- La whitelist de usuarios autorizados no debe estar en el código fuente

---

## 5. Control de Acceso (A01:2021 — Broken Access Control)

### 5.1 Proteger todas las rutas [OBLIGATORIO]

```python
# ✅ CORRECTO — verificar auth en cada ruta protegida
@app.route("/inventory")
def inventory():
    if "user_email" not in session:
        return redirect(url_for("login"))

# Preferible — decorador reutilizable (pendiente implementar)
@app.route("/inventory")
@require_auth
def inventory():
    ...
```

### 5.2 RBAC — Roles por recurso [OBLIGATORIO para rutas administrativas]

```python
# Roles definidos en roles.json (pendiente implementar)
# admin: acceso total
# dashboard_user: solo /dashboard y /analytics
# basic_user: solo /inventory (lectura)
```

### 5.3 Prohibiciones [OBLIGATORIO]

- No exponer IDs secuenciales en URLs sin verificar pertenencia al usuario
- No hacer diferencia entre "recurso no encontrado" y "sin acceso" en mensajes de error
- No confiar en campos `hidden` en formularios HTML para lógica de autorización

---

## 6. Cabeceras de Seguridad HTTP (A05:2021 — Misconfig)

Flask-Talisman ya está configurado. Verificar que `talisman()` esté inicializado con:

```python
# ✅ Mínimas cabeceras requeridas (ya implementadas)
Talisman(app,
    force_https=False,          # True en producción
    content_security_policy=csp,
    frame_options="DENY",
    referrer_policy="strict-origin-when-cross-origin",
)
```

Las siguientes cabeceras **siempre deben estar presentes** en respuestas:

| Cabecera | Valor recomendado |
|----------|------------------|
| `X-Content-Type-Options` | `nosniff` |
| `X-Frame-Options` | `DENY` |
| `X-XSS-Protection` | `1; mode=block` |
| `Referrer-Policy` | `strict-origin-when-cross-origin` |
| `Content-Security-Policy` | Definir explícitamente orígenes permitidos |

---

## 7. Manejo de Errores y Logging (A09:2021 — Logging failures)

### 7.1 No exponer stack traces al usuario [OBLIGATORIO]

```python
# ✅ CORRECTO
@app.errorhandler(500)
def server_error(e):
    current_app.logger.error(f"Internal error: {e}", exc_info=True)
    return render_template("error.html", message="Error interno"), 500

# ❌ PROHIBIDO en producción
app.config["DEBUG"] = True   # expone stack traces completos
```

### 7.2 Qué logear [OBLIGATORIO]

```python
# Eventos de seguridad que SIEMPRE deben logearse:
logger.warning("AUTH_FAILURE: usuario no autorizado", extra={"email": email})
logger.warning("SESSION_EXPIRED: sesión expirada", extra={"user": user})
logger.warning("SESSION_HIJACK: fingerprint no coincide")
logger.info("AUTH_SUCCESS: login exitoso", extra={"email": email})
logger.info("LOGOUT: cierre de sesión", extra={"user": user})
logger.info("EXPORT: exportación iniciada", extra={"user": user, "format": fmt})
```

### 7.3 Qué NO logear [OBLIGATORIO]

```python
# ❌ PROHIBIDO — datos sensibles en logs
logger.info(f"Usuario: {email}, contraseña: {password}")
logger.debug(f"Token: {token}")
logger.debug(f"SECRET_KEY = {app.secret_key}")
```

---

## 8. Dependencias y Supply Chain (A06:2021 — Vulnerable Components)

### 8.1 Auditoría de dependencias [OBLIGATORIO antes de cada release]

```bash
# Verificar vulnerabilidades conocidas
pip install safety
safety check --file requirements.txt

# Análisis estático de seguridad
pip install bandit
bandit -r . -x tests/ -f txt
```

### 8.2 Actualización de dependencias

- Revisar vulnerabilidades **mensualmente** con `safety check`
- Actualizar dependencias con CVE críticos en máximo **72 horas**
- Documentar en el PR el resultado del `safety check`

### 8.3 `requirements.txt` [OBLIGATORIO]

- Versiones **pinneadas** (`Flask==3.0.2`, no `Flask>=2.0`)
- Incluir hash de integridad para producción: `pip download --require-hashes`

---

## 9. Datos Sensibles y Criptografía (A02:2021 — Crypto Failures)

### 9.1 HTTPS [OBLIGATORIO en producción]

```python
# app.py — producción
Talisman(app, force_https=True)
```

### 9.2 Datos en tránsito

- Toda comunicación con Odoo debe ser sobre HTTPS/XMLRPC-secure
- No almacenar credenciales de Odoo en cookies

### 9.3 Datos en reposo

- No almacenar datos de inventario con PII en texto plano
- Base de datos PostgreSQL: habilitar cifrado en disco en producción

---

## 10. Rate Limiting y DoS (A04:2021 — Insecure Design)

### 10.1 Endpoints críticos [OBLIGATORIO]

```python
# Flask-Limiter — pendiente implementar, requerido antes de producción
@limiter.limit("5 per minute")
def google_oauth_callback(): ...

@limiter.limit("10 per hour")
def export_excel(): ...

@limiter.limit("30 per minute")
def inventory(): ...
```

---

## 11. Checklist Rápida Pre-Commit

Antes de cada commit, verificar:

- [ ] No hay credenciales hardcodeadas (`grep -r "password\|secret\|token" .` sin resultados sensibles)
- [ ] No hay `DEBUG = True` para producción
- [ ] No hay `| safe` en templates sin justificación
- [ ] No hay concatenación de strings en SQL
- [ ] Cada nueva ruta tiene control de acceso
- [ ] Los tests pasan: `.\venv\Scripts\python.exe -m pytest tests/ -v`

---

## 12. Herramientas Recomendadas

| Herramienta | Propósito | Comando |
|-------------|-----------|---------|
| `bandit` | SAST - análisis estático Python | `bandit -r . -x tests/` |
| `safety` | SCA - vulnerabilidades en dependencias | `safety check -r requirements.txt` |
| `pytest` | Tests unitarios e integración | `.\venv\Scripts\python.exe -m pytest tests/ -v` |
| `pytest-cov` | Cobertura de tests | `--cov=. --cov-report=html` |

---

## 13. Referencias

- [OWASP Top 10 2021](https://owasp.org/Top10/)
- [CWE Top 25 (2023)](https://cwe.mitre.org/top25/archive/2023/2023_top25_list.html)
- [Flask Security Guide](https://flask.palletsprojects.com/en/latest/security/)
- [Python Security Best Practices (CERT)](https://wiki.sei.cmu.edu/confluence/display/python)
- ISO 27001:2013 Annex A.14 — System acquisition, development and maintenance

---

*Documento aprobado para uso interno. Revisar anualmente o ante cambios de stack tecnológico.*
