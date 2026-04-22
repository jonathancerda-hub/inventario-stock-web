## Descripción

<!-- Describe brevemente los cambios que introduce este PR -->

**Tipo de cambio:**
- [ ] Bug fix
- [ ] Nueva funcionalidad
- [ ] Refactoring
- [ ] Mejora de seguridad
- [ ] Documentación

---

## ✅ Checklist de Seguridad (OBLIGATORIO)

> Estas verificaciones son **requeridas** antes de aprobar el PR.  
> Referencia: [SECURE_CODING_GUIDELINES.md](../docs/SECURE_CODING_GUIDELINES.md)

### 🔐 Secretos y Credenciales
- [ ] No hay credenciales, tokens ni API keys hardcodeadas en el código
- [ ] No hay valores sensibles en logs o mensajes de error
- [ ] Los nuevos secretos se leen desde variables de entorno (`.env`)

### 🛡️ Validación de Entradas
- [ ] Todas las entradas de usuario son validadas (tipo, longitud, formato)
- [ ] No hay concatenación de strings para construir queries SQL
- [ ] No se usa `| safe` en templates Jinja2 sin justificación documentada

### 🔑 Autenticación y Sesiones
- [ ] Las nuevas rutas tienen control de acceso (`session["user_email"]` o `@require_auth`)
- [ ] No se expone información diferente entre "no encontrado" y "sin acceso"
- [ ] El logout limpia la sesión completamente con `session.clear()`

### 📦 Dependencias
- [ ] Las nuevas dependencias están pinneadas con versión exacta en `requirements.txt`
- [ ] Se ejecutó `safety check -r requirements.txt` sin vulnerabilidades críticas

### 🧪 Tests
- [ ] Los tests existentes pasan: `.\venv\Scripts\python.exe -m pytest tests/ -v`
- [ ] Se agregaron tests para la nueva funcionalidad (si aplica)
- [ ] La cobertura no disminuyó respecto al PR anterior

### 📋 Cabeceras HTTP (solo si se modificó `app.py` o configuración)
- [ ] Flask-Talisman sigue activo y configurado
- [ ] `DEBUG = False` en todos los entornos de producción

---

## 🔍 Resultado de Safety Check

```
# Pegar salida de: safety check -r requirements.txt
```

---

## 🧪 Tests ejecutados

```
# Pegar salida de: .\venv\Scripts\python.exe -m pytest tests/ -v --tb=short
```

---

## 📝 Notas adicionales

<!-- Cualquier contexto, decisiones de diseño, o riesgos conocidos -->
