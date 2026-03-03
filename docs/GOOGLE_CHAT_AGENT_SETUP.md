# 🤖 Configuración de Agente IA para Inventario en Google Chat

## 📋 Documento para Equipo de IT / Administradores de Google Workspace

**Proyecto:** Agente Inteligente de Consultas de Inventario  
**Fecha:** Febrero 2026  
**Solicitante:** Jonathan Cerda  
**Empresa:** AgrovetMarket

---

## 🎯 Objetivo del Proyecto

Implementar un agente inteligente (chatbot con IA) en Google Chat que permita a los usuarios consultar información del inventario de la empresa usando lenguaje natural.

### Ejemplos de Uso:

```
Usuario: "¿Cuánto stock tenemos de vitaminas en Lima?"
Agente: [Respuesta con datos actuales del sistema]

Usuario: "Muéstrame productos que vencen este mes"
Agente: [Lista de productos críticos con análisis]
```

---

## ✅ Requisitos Previos (Ya Cumplidos)

- ✅ Google Workspace Business Standard o superior
- ✅ Gemini for Workspace activo
- ✅ Dominio corporativo: @agrovetmarket.com
- ✅ Sistema de inventario existente (Flask + Odoo)

---

## 🔍 Verificaciones Necesarias

### 1. Acceso a Google Cloud Console

**Responsable:** Administrador de Google Workspace  
**URL:** https://console.cloud.google.com

#### Pasos:

1. Iniciar sesión con cuenta de administrador
2. Verificar que exista un proyecto o crear uno nuevo:
   - **Nombre sugerido:** `inventario-agente-ia`
3. Anotar el **Project ID** (necesario para la implementación)

#### ✅ Checklist:
- [ ] Acceso a Google Cloud Console confirmado
- [ ] Project ID obtenido: `___________________________`

---

### 2. Verificar Créditos y Facturación de Google Cloud

**Ubicación:** Console → Billing → Credits

#### Información a Verificar:

1. **Créditos Disponibles:**
   - Muchos contratos Enterprise incluyen $500-$2000/mes en créditos
   - Verificar si hay créditos activos: Console → Billing → Credits
   
2. **Cuenta de Facturación:**
   - Confirmar que existe una cuenta de facturación activa
   - Necesaria aunque tengamos créditos

3. **Presupuesto/Alertas:**
   - Configurar alerta si el gasto supera $50/mes
   - Console → Billing → Budgets & Alerts

#### ✅ Checklist:
- [ ] Créditos disponibles: $_____________ / mes
- [ ] Cuenta de facturación activa: Sí / No
- [ ] Alertas de presupuesto configuradas: Sí / No

---

### 3. Habilitar APIs Necesarias

**Ubicación:** Console → APIs & Services → Library

#### APIs Requeridas:

```
1. Vertex AI API
   - Para usar Gemini (modelo de IA)
   - URL: https://console.cloud.google.com/apis/library/aiplatform.googleapis.com
   
2. Google Chat API
   - Para crear el bot
   - URL: https://console.cloud.google.com/apis/library/chat.googleapis.com
   
3. Cloud Resource Manager API
   - Para gestión de proyectos
   - URL: https://console.cloud.google.com/apis/library/cloudresourcemanager.googleapis.com
```

#### Pasos para Habilitar:

1. Ir a Console → APIs & Services → Library
2. Buscar cada API por nombre
3. Click en "Enable" / "Habilitar"
4. Esperar confirmación (puede tomar 1-2 minutos)

#### ✅ Checklist:
- [ ] Vertex AI API habilitada
- [ ] Google Chat API habilitada
- [ ] Cloud Resource Manager API habilitada

---

### 4. Configurar Permisos (IAM)

**Ubicación:** Console → IAM & Admin → IAM

#### Permisos Necesarios para el Desarrollador:

Usuario: **jonathan.cerda@agrovetmarket.com**

Roles requeridos:
```
1. Vertex AI User
   - Para usar Gemini API
   
2. Chat Bot Admin
   - Para configurar el bot en Google Chat
   
3. Service Account Creator (opcional)
   - Para crear credenciales si es necesario
```

#### Pasos:

1. IAM & Admin → IAM
2. Click "+ Grant Access"
3. Agregar email: jonathan.cerda@agrovetmarket.com
4. Asignar roles listados arriba
5. Save

#### ✅ Checklist:
- [ ] Usuario agregado al proyecto
- [ ] Roles asignados correctamente
- [ ] Permisos verificados

---

### 5. Verificar Pricing de Vertex AI (Gemini)

**Ubicación:** Console → Vertex AI → Pricing

#### Información Importante:

Con **Google Workspace Business Standard + Gemini activo**, verificar:

1. **Pricing Corporativo:**
   - ¿Tienen descuento corporativo en Vertex AI?
   - ¿Gemini está incluido en el plan?

2. **Límites y Cuotas:**
   - Console → IAM & Admin → Quotas
   - Buscar "Vertex AI API"
   - Anotar límites de requests por minuto

3. **Modelo Recomendado:**
   ```
   Gemini 1.5 Flash (más económico):
   - Input:  $0.075 / 1M tokens
   - Output: $0.30 / 1M tokens
   - Ideal para consultas rápidas
   
   Estimación: ~$5-20/mes con uso moderado
   (puede ser $0 si está incluido en su plan)
   ```

#### ✅ Checklist:
- [ ] Pricing verificado
- [ ] Descuentos corporativos: Sí / No / Desconocido
- [ ] Cuotas suficientes para el proyecto

---

### 6. Generar Credenciales (Service Account)

**Ubicación:** Console → IAM & Admin → Service Accounts

#### Pasos:

1. Click "Create Service Account"
2. Nombre: `inventario-bot-agent`
3. Descripción: "Agente IA para consultas de inventario"
4. Roles a asignar:
   - Vertex AI User
   - Chat Bot Admin
5. Click "Create and Continue"
6. Click "Done"
7. Crear Key:
   - Click en el service account creado
   - Keys → Add Key → Create new key
   - Tipo: JSON
   - Descargar archivo JSON

#### ⚠️ Seguridad:
- El archivo JSON contiene credenciales sensibles
- Entregar de forma segura al desarrollador
- NO compartir por email sin encriptar
- NO subir a repositorios públicos

#### ✅ Checklist:
- [ ] Service Account creado
- [ ] Archivo JSON descargado
- [ ] Credenciales entregadas de forma segura

---

## 📊 Estimación de Costos

### Escenario Esperado:

```
Usuarios consultando el agente: ~50-100 consultas/día

Costos Estimados:

Con Vertex AI (Gemini Flash):
├─ Mes 1 (pruebas): ~$5-10
├─ Meses siguientes: ~$15-25/mes
└─ Con créditos corporativos: Posiblemente $0

Infraestructura:
├─ Render (actual): $0 (tier gratuito)
├─ Google Chat: $0 (incluido en Workspace)
└─ APIs Google: Ver arriba

TOTAL ESTIMADO: $0-25/mes
```

### Controles de Costo Recomendados:

1. **Configurar Budget Alert:** $50/mes
2. **Límite de Requests:** 1000 requests/día
3. **Revisión mensual:** Analizar uso real

---

## 🏗️ Arquitectura Técnica

```
┌─────────────────────────────────────────────┐
│ Usuario (@agrovetmarket.com)                │
│ escribe en Google Chat                      │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│ Bot en Google Chat                          │
│ (configurado en Google Cloud)               │
└─────────────────┬───────────────────────────┘
                  │ Webhook
                  ▼
┌─────────────────────────────────────────────┐
│ Flask App en Render (actual)                │
│ - Recibe mensaje del usuario                │
│ - Procesa comando/pregunta                  │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│ Gemini API (Vertex AI)                      │
│ - Interpreta pregunta en lenguaje natural   │
│ - Decide qué consultar                      │
│ - Genera respuesta inteligente              │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│ Odoo (Sistema actual)                       │
│ - Consulta stock real                       │
│ - Datos de productos                        │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
           Respuesta al Usuario
```

---

## 📝 Información Adicional para IT

### Seguridad y Compliance:

- ✅ **Datos sensibles:** No se almacenan datos de inventario en Google
- ✅ **Autenticación:** Solo usuarios @agrovetmarket.com pueden usar el bot
- ✅ **Logs:** Todas las consultas se registran en analytics
- ✅ **HTTPS:** Toda comunicación encriptada
- ✅ **Tokens:** Credenciales rotables mensualmente

### Monitoreo:

1. **Google Cloud Monitoring:**
   - Dashboard de uso de APIs
   - Alertas de errores
   
2. **Logs Centralizados:**
   - Cloud Logging para debugging
   - Retención: 30 días

3. **Analytics Personalizado:**
   - Sistema actual de analytics del proyecto
   - Métricas de uso del bot

---

## 🚀 Próximos Pasos

### Para el Equipo de IT:

1. ✅ Completar todos los checkboxes de este documento
2. ✅ Generar y entregar credenciales (Service Account JSON)
3. ✅ Confirmar presupuesto aprobado (~$25/mes máximo)
4. ✅ Coordinar fecha de pruebas con usuarios piloto

### Para el Desarrollador:

1. Recibir credenciales de forma segura
2. Implementar agente con Gemini API
3. Configurar bot en Google Chat
4. Realizar pruebas internas
5. Deploy a producción
6. Monitorear primeros 7 días

---

## 📞 Contactos

**Desarrollador del Proyecto:**  
- Nombre: Jonathan Cerda  
- Email: jonathan.cerda@agrovetmarket.com  
- Rol: Product Owner / Desarrollador

**Equipo de IT / Admin Google Workspace:**  
- Nombre: ______________________________________  
- Email: ______________________________________  
- Rol: Administrador GCP / Workspace Admin

---

## 📚 Referencias Útiles

- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [Google Chat API](https://developers.google.com/chat)
- [Gemini Pricing](https://cloud.google.com/vertex-ai/generative-ai/pricing)
- [Google Workspace Integration](https://developers.google.com/workspace)

---

## ✅ Checklist Final

### Antes de Comenzar Implementación:

- [ ] Todas las APIs habilitadas
- [ ] Service Account creado y configurado
- [ ] Credenciales JSON descargadas
- [ ] Permisos de IAM asignados
- [ ] Budget alerts configuradas
- [ ] Project ID compartido con desarrollador
- [ ] Presupuesto mensual aprobado
- [ ] Fecha de inicio coordinada

### Firma de Aprobación:

```
IT Manager / Admin GCP:
Nombre: _________________________________
Firma: __________________________________
Fecha: __________________________________

Desarrollador:
Nombre: Jonathan Cerda
Fecha: _______________
```

---

**Fecha de Creación:** 24 de febrero de 2026  
**Versión:** 1.0  
**Última Actualización:** 24/02/2026
