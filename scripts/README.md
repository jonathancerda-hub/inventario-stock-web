# 🔧 Scripts

Scripts de utilidad para mantenimiento y operaciones del sistema.

## Archivos

### `migrate_data_to_pro.py`
Script para migración de datos de Supabase Free a Supabase Pro.

**Uso:**
```bash
python scripts/migrate_data_to_pro.py
```

**Requiere:**
- Variables de entorno configuradas para ambas bases de datos
- Conexión activa a Supabase Free (origen) y Pro (destino)

**Referencias:** Ver [docs/PLAN_MIGRACION_SUPABASE_PRO.md](../docs/PLAN_MIGRACION_SUPABASE_PRO.md)

---

### `validate_migration.py`
Valida la integridad de la migración comparando registros entre BD origen y destino.

**Uso:**
```bash
python scripts/validate_migration.py
```

**Validaciones:**
- ✅ Conteo de registros coincidente
- ✅ Integridad de datos (checksums)
- ✅ Disponibilidad de ambas bases de datos

**Salida:** Reporte de validación con estadísticas comparativas

---

## Estructura

```
scripts/
├── README.md                    # Este archivo
├── migrate_data_to_pro.py      # Script de migración
└── validate_migration.py        # Script de validación
```

## Notas

- Ejecutar siempre desde la raíz del proyecto
- Verificar variables de entorno antes de ejecutar
- Los scripts incluyen logging detallado
