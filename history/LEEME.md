# ATLAS Development Team — prueba integral

Resultado final de SENTINEL: **passed_with_observations**. Proyecto ATLAS-SN-QA-20261002, plugin 0.4.0.

## Abrir el dashboard

Abrir `deliverables/implementation/v1.1/dashboard.html` en un navegador. Es autocontenido: no requiere instalación, servidor ni conexión. La copia `ServiceNow_dashboard_v1.1.html` entregada por separado tiene exactamente los mismos bytes auditados.

## Historial

| Artefacto | Versión | Resultado |
|---|---|---|
| PROJECT_SPEC | 1.0 | ATLAS definió alcance y reglas; conservado sin cambios |
| DATA_SPEC | 1.0 | NEXUS inspeccionó Excel y definió reglas reproducibles; conservado sin cambios |
| Implementación / DEV_REPORT | 1.0 | Primera entrega de ensayo, partial, defecto reservado |
| QA_REPORT | 1.0 | failed; SENTINEL detectó QA-001 independientemente |
| Implementación / DEV_REPORT | 1.1 | FORGE corrigió QA-001; nueva versión, sin sobrescribir v1.0 |
| QA_REPORT | 1.1 | passed_with_observations; segunda auditoría y cierre del hallazgo |

## Hallazgo y corrección

QA-001: el filtro SCTASK usaba RITM. En la primera interfaz mostraba 35 tickets canónicos, 24 backlog y 19 sin actualización; lo esperado era 13, 7 y 6. Fallaban 8 de las 32 selecciones de filtros. La corrección elimina la sustitución del valor seleccionado. La segunda auditoría prueba las 32 selecciones, restablecimiento y 9 casos de fechas, además de fuente, contratos y versiones históricas.

El detalle del defecto se conservó reservado hasta la emisión de QA_REPORT 1.0 y luego se incorporó en `controlled_defect_disclosure.json`. SENTINEL se ejecutó en un agente con contexto independiente y declaró no consultar el registro reservado. El aislamiento fue de contexto e instrucciones; no una barrera de permisos del sistema de archivos compartido.

## Indicadores globales al 01/10/2026 18:00

| Indicador | Resultado |
|---|---:|
| Filas fuente | 102 |
| Tickets canónicos | 100 |
| Backlog | 64 |
| Sin actualización >48h | 52 |
| No evaluables para actualización dentro del backlog | 5 |
| Sin responsable dentro del backlog | 6 |
| Sin grupo dentro del backlog | 2 |
| Antigüedad media del backlog evaluable | 21,04 días |

Los no evaluables siguen identificados y no desaparecen del backlog ni de las métricas que no requieren sus fechas. No se convierten en ceros ni en tickets sin actualización.

## Supuestos y alcance

Ante la ausencia de un nuevo adjunto en el mensaje se utilizó el Excel más reciente disponible, `nexus_servicenow_test_v1(3).xlsx`, una fuente simulada de prueba. Los KPIs auxiliares se calculan sobre backlog. La selección de una versión por ticket duplicado y los demás supuestos A1/A2/A4/A5 siguen siendo provisionales, visibles en contratos e interfaz; no se presentan como reglas confirmadas por el usuario. Los dos IDs duplicados están fuera del backlog, por lo que no alteran esos totales operativos.

La auditoría valida este prototipo contra estos contratos. QA-002 es una observación no bloqueante: dos medias calculadas en Python y JavaScript difieren aproximadamente 7e-15 y 4e-15 días por aritmética IEEE; la interfaz coincide al redondear a dos decimales. Se conserva la comparación exploratoria binaria fallida; esa igualdad no era un criterio contractual. No se requiere corrección para este prototipo. No constituye certificación de producción ni auditoría completa de accesibilidad. Consultar `qa/QA_REPORT_v1.1.json` para cobertura, limitaciones y observaciones exactas.

## Contenido del paquete

- `deliverables/contracts/`: PROJECT_SPEC y DATA_SPEC.
- `deliverables/reports/`: DEV_REPORT 1.0 y 1.1.
- `deliverables/qa/`: QA_REPORT 1.0 y 1.1, cálculos propios, pruebas en Chromium, capturas y evidencia.
- `deliverables/implementation/`: ambas versiones, código, generadores y pruebas FORGE.
- `deliverables/analysis/` y `data/`: perfil NEXUS, resultados esperados y registros con trazabilidad.
- `deliverables/source/` e `input/`: Excel fuente; la segunda ruta conserva la estructura necesaria para repetir los scripts originales.
- `deliverables/ATLAS_*.json`, hashes e historial: coordinación, asignación y cierre.

## Reproducir las verificaciones

Desde la raíz extraída, Python con openpyxl permite ejecutar `python deliverables/qa/recalculate.py`. Las pruebas de navegador requieren Node, Playwright y Chromium. Configurar `CODEX_PRIMARY_RUNTIME_NODE_MODULES` al directorio que contiene Playwright y `CHROMIUM_EXECUTABLE_PATH` al ejecutable de Chromium, y ejecutar `node deliverables/qa/browser_audit.cjs 1.1`. Los scripts documentan los parámetros del entorno original. Ejecutar en una copia para no sobrescribir evidencia histórica. No es necesario ejecutar ninguna prueba para abrir el dashboard.
