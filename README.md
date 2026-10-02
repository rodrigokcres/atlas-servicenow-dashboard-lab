# ATLAS ServiceNow Dashboard Lab

Dashboard de gestión de tickets de ServiceNow. Proyecto: `servicenow-gestion-tickets`.

## Cambio v1.2: filtro de prioridad

Abra `src/v1.2/dashboard.html` directamente en un navegador. No requiere servidor, instalación ni conexión a ServiceNow. Contiene datos sintéticos de prueba.

El filtro **Todas las prioridades / P1 / P2 / P3 / P4** se combina con tipo de ticket y grupo resolutor. Las tarjetas, gráficos, distribución por grupo, antigüedad, detalle y registros no evaluables usan la misma selección. **Restablecer** limpia los tres filtros.

Se mantienen corte `01/10/2026 18:00`, reglas de backlog y >48 horas, deduplicación, tratamiento de fechas y supuestos provisionales de v1.1.

## Contratos y trazabilidad

| Artefacto | Contrato de esta entrega | Motivo |
| --- | --- | --- |
| PROJECT_SPEC | `specs/PROJECT_SPEC_v1.1.json` | Nuevo requisito funcional y flujo Git |
| DATA_SPEC | `specs/DATA_SPEC_v1.1.json` | Añadir dimensión prioridad y ampliar T6 a tres filtros; KPIs intactos |
| DEV_REPORT | `reports/DEV_REPORT_v1.2.json` | Implementación v1.2 y pruebas FORGE |
| QA_REPORT | `reports/QA_REPORT_v1.2.json` | Auditoría independiente SENTINEL; consultar su estado real |

La base validada se conserva sin reescrituras en `history/`: contratos 1.0, implementaciones 1.0/1.1 e informes históricos. `changes/CR-002-priority.json` autoriza el cambio; `changes/historical-sha256.json` conserva las huellas del paquete completo original.

El paquete histórico usa el identificador `ATLAS-SN-QA-20261002`, distinto del ID `servicenow-gestion-tickets` indicado por el usuario y el README original. La correspondencia está documentada explícitamente en `PROJECT_SPEC 1.1`; no se han cambiado los identificadores de los documentos históricos.

## Git

- Base de la rama: `main` en `b27ca326c4fc6d6907e64bcb33f8df88437dc3b2`.
- Rama de trabajo: `feat/priority-filter-v1.2`.
- Commit de recuperación histórica: `797f6d52c497c7625364f88df6e37f658b59267b`.
- El `main` inicial contenía solo documentación; la v1.1 validada se recuperó del paquete original, no de un tag inexistente.
- Cambios y QA se preparan en esta rama. No hay merge ni despliegue automático.

## Construcción y comprobación

```bash
python3 src/v1.2/build.py
```

El build usa los campos originales sintéticos conservados en `history/data/normalized_tickets.json`; las reglas se ejecutan en `core.js`. Las instrucciones de QA y su evidencia quedan en `qa/` y el informe SENTINEL. Las pruebas requieren Python/openpyxl, Node.js/Playwright y un Chromium disponible; consulte los scripts para las variables de entorno.

## Fuente y evidencia histórica

El Excel original y las capturas binarias históricas no se incorporan a Git. El paquete `ATLAS_ServiceNow_prueba_integral(1).zip` conserva esas evidencias. Para repetir la auditoría desde fuente, coloque el Excel original, sin modificar, en `history/source/nexus_servicenow_test_v1.xlsx`; SHA-256 esperado: `a9e51e2eeb45c44df7cb8fc2636924bbf704952142e26c2239a2e7baae938a2c`.

Los informes y manifiestos históricos mantienen rutas de su contexto original. Los scripts históricos se conservan como evidencia y no se presentan como portables; utilice los scripts nuevos para esta entrega. El HTML de prueba incluye registros sintéticos, no datos productivos.

### Repetir la auditoría independiente

Para la comprobación completa de integridad histórica, restaure también las capturas PNG del paquete original en sus rutas `history/`; este directorio corresponde al contenido de `deliverables/` del ZIP. El manifiesto incluye esos binarios y el script no los omite. Sin ellos, puede ejecutar las pruebas de navegador con el oráculo conservado, pero no afirmar una nueva conciliación desde el Excel ni una verificación completa del paquete.

Con la fuente y el paquete histórico disponibles:

```bash
python3 qa/independent_oracle.py
python3 qa/integrity_v1.2.py
# Ajustar estas dos rutas a la instalación local.
export CODEX_PRIMARY_RUNTIME_NODE_MODULES=/ruta/a/node_modules
export ATLAS_BROWSER=/ruta/a/chrome-headless-shell
node qa/browser_audit_v1.2.cjs
```

Resultado de SENTINEL para v1.2: **passed_with_observations**. Pasaron las 160 combinaciones, 32 regresiones contra v1.1, restablecimiento, selecciones vacías, bordes de fechas y vista móvil. La observación histórica QA-002 corresponde a diferencias internas IEEE-754 de medias frente a Python (máximo 3,55e-15 días); no se ocultó con tolerancias y las representaciones visibles coinciden. Consulte el informe independiente para el alcance y evidencia exactos.
