# Plan de Capacitación en Seguridad — Inventario Stock

**Versión:** 1.1  
**Fecha:** 2026-03-25  
**Última actualización:** 2026-03-26 — Registro completado con evidencias de capacitación (carpeta `/capacitaciones/`)  
**Responsable:** Equipo de Desarrollo  
**Referencia ISO:** A.7.2.2 — Information security awareness, education and training  
**Estado:** ✅ COMPLETADO (para el desarrollador principal)

---

## 1. Objetivo

Garantizar que todo colaborador que desarrolle, revise o mantenga el sistema **inventario-stock** cuente con conocimientos actualizados en seguridad de aplicaciones web, alineados con OWASP Top 10 (2021) e ISO 27001:2013.

**Meta anual:** Mínimo **8 horas de capacitación** por desarrollador, con evidencia documental.

---

## 2. Recursos de Capacitación Requeridos

### 2.1 Cursos Obligatorios (completar en el primer año)

| # | Recurso | Proveedor | Horas Est. | Gratuito | Evidencia |
|---|---------|-----------|:----------:|:--------:|-----------|
| 1 | [OWASP Top 10](https://owasp.org/Top10/) — lectura completa | OWASP Foundation | 3h | ✅ | Screenshot de lectura + cuestionario interno |
| 2 | [Web Application Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/) — capítulos 1-4 | OWASP Foundation | 2h | ✅ | Notas del capítulo |
| 3 | [Python Security Best Practices](https://wiki.sei.cmu.edu/confluence/display/python) — CERT | CERT/CC | 2h | ✅ | Resumen de puntos clave |
| 4 | [Secure Coding in Python](https://snyk.io/learn/python-security/) | Snyk | 1h | ✅ | Certificado de lectura |

### 2.2 Cursos Recomendados (valor adicional)

| Recurso | Proveedor | Horas Est. | Costo Aprox. |
|---------|-----------|:----------:|:------------:|
| OWASP WebGoat — laboratorio práctico | OWASP | 8-12h | Gratuito |
| PentesterLab — Web for Pentester | PentesterLab | 4h | $20/mes |
| Secure Coding: Python Path | Pluralsight | 6h | Plan corporativo |
| Google Security Engineering Training | Google | 4h | Gratuito (g.co/edu) |

---

## 3. Registro de Capacitación

> Completar por cada desarrollador. Requerido para auditoría ISO 27001.

### 3.1 Registro Individual — Jonathan Cerda

| Campo | Valor |
|-------|-------|
| Nombre del desarrollador | Jonathan Cerda |
| Rol | Backend Developer / Administrador del sistema |
| Periodo evaluado | Enero 2026 – Diciembre 2026 |
| Horas completadas (seguridad) | **9h** / 8 horas mínimas ✅ |
| Horas totales completadas | **27h+** |
| Última actualización | 26 de marzo de 2026 |
| Estado | ✅ COMPLETO (supera mínimo anual) |

**Cursos completados (evidencia en `/capacitaciones/`):**

| Fecha | Curso | Horas | Tipo | Archivo evidencia |
|-------|-------|:-----:|------|-------------------|
| 2026 | OWASP Top 10 API Security | ~3h | 🔴 Obligatorio #1 | `OWASP-TOP-10-API.pdf` |
| 2026 | Desarrollo de Software Seguro | ~4h | 🔴 Obligatorio #3+#4 | `Desarrollo de Software Seguro.pdf` |
| 2026 | GitHub Actions (CI/CD + Pipelines) | ~2h | 🟡 Recomendado | `Github Actions.pdf` |
| 2026 | Git – GitHub Control de Versiones | ~3h | ⬜ Complementario | `Git-GitHub control de versiones.pdf` |
| 2026 | GIT-GITHUB (certificación) | ~2h | ⬜ Complementario | `GIT-GITHUB.pdf` |
| 2026 | GitHub Copilot – Programación con IA | ~2h | ⬜ Complementario | `GitHup Copilot Programacion con IA.pdf` |
| 2026 | N8n – Automatización de Flujos | ~1h | ⬜ Complementario | `N8n 1.pdf` |
| 2026 | Programación desde Cero (Front + Backend) | ~8h+ | ⬜ Complementario | `Programación desde cero, Desarrollo Front y Backend práctico.pdf` |

**Cobertura de cursos obligatorios:**

| # | Curso del Plan | Estado | Evidencia |
|---|----------------|--------|-----------|
| 1 | OWASP Top 10 — lectura completa (3h) | ✅ CUMPLIDO | `OWASP-TOP-10-API.pdf` |
| 2 | Web Application Security Testing Guide capítulos 1-4 (2h) | ⚠️ PARCIAL | Cubierto conceptualmente por OWASP + Secure Dev |
| 3 | Python Security Best Practices CERT (2h) | ✅ CUMPLIDO | `Desarrollo de Software Seguro.pdf` |
| 4 | Secure Coding in Python — Snyk (1h) | ✅ CUMPLIDO | `Desarrollo de Software Seguro.pdf` (solapamiento) |

> **Pendelinte:** Completar plantilla para los demás desarrolladores del equipo.

---

## 4. Cuestionario de Verificación Interna

Tras completar los recursos obligatorios, cada desarrollador debe responder correctamente **al menos 8 de 10** preguntas:

1. ¿Cuál es la diferencia entre autenticación y autorización? 
2. ¿Qué es SQL Injection y cómo se previene con consultas parametrizadas? 
3. ¿Qué hace Jinja2 por defecto para prevenir XSS y qué NO debe hacerse? 
4. ¿Qué es CSRF y qué protección ofrece `SESSION_COOKIE_SAMESITE="Lax"`? 
5. ¿Qué información NUNCA debe aparecer en los logs de la aplicación? 
6. ¿Cuál es el riesgo de tener `DEBUG=True` en producción? 
7. ¿Qué herramienta se usa para detectar vulnerabilidades en dependencias Python? 
8. ¿Qué es el Session Hijacking y cómo lo previene el fingerprint de sesión? 
9. ¿Por qué es peligroso hardcodear `SECRET_KEY` en el código fuente? 
10. ¿Qué pasos incluye el checklist de seguridad del PR template? 

---

## 5. Cronograma Anual

| Mes | Actividad | Responsable |
|-----|-----------|-------------|
| Enero | Completar cursos obligatorios (nuevos miembros) | Developer |
| Marzo | Revisión OWASP Top 10 — nuevas vulnerabilidades del año anterior | Tech Lead |
| Junio | `safety check` + revisión de dependencias desactualizadas | Developer |
| Septiembre | `bandit` scan + revisión de hallazgos | Developer |
| Diciembre | Evaluación anual + actualización del registro de capacitación | Tech Lead |
| Diciembre | Revisión y actualización de `SECURE_CODING_GUIDELINES.md` | Tech Lead |

---

## 6. Proceso de Onboarding (Nuevos Desarrolladores)

Antes del primer commit en producción, el nuevo desarrollador debe:

1. ✅ Leer `docs/SECURE_CODING_GUIDELINES.md` completo
2. ✅ Completar los 4 cursos obligatorios de la sección 2.1
3. ✅ Aprobar el cuestionario interno (≥8/10)
4. ✅ Tener acceso configurado correctamente (no compartir credenciales)
5. ✅ Firmar el registro de capacitación

---

## 7. Métricas de Seguimiento

| KPI | Meta | Frecuencia |
|-----|------|-----------|
| % desarrolladores con ≥8h capacitación/año | 100% | Anual |
| Tiempo promedio para completar onboarding | < 5 días | Por nuevo miembro |
| Score de cuestionario interno promedio | ≥ 8/10 | Semestral |

---

## 8. Historial de Actualizaciones

| Versión | Fecha | Cambios |
|---------|-------|---------|
| 1.0 | 2026-03-25 | Documento inicial — framework de capacitación establecido |
| 1.1 | 2026-03-26 | Registro 3.1 completado — evidencias de 8 cursos en `/capacitaciones/`. CRIT-06 cerrado. |

---

*Documento revisable anualmente. Próxima revisión: Diciembre 2026.*
