# Auditoría independiente SENTINEL v1.2

Implementación auditada: commit `8132a4f12984cf03f7ec2175a5f83a81ae2cc113`, hashes en `integrity_v1.2.json`.

Requisitos: Python con openpyxl; Node.js con Playwright; Chromium. `CODEX_PRIMARY_RUNTIME_NODE_MODULES` debe apuntar al directorio node_modules donde está Playwright. `ATLAS_BROWSER` permite indicar el ejecutable Chromium; si no se configura, se usa la ruta temporal original de la auditoría.

```bash
python qa/independent_oracle.py
ATLAS_BROWSER=/ruta/a/chromium node qa/browser_audit_v1.2.cjs
python qa/integrity_v1.2.py
node qa/precision_v1.2.cjs
```

La auditoría de datos requiere restaurar el Excel original en `history/source/nexus_servicenow_test_v1.xlsx`. La comprobación completa `integrity_v1.2.py` requiere **todos los archivos del paquete original**, también sus PNG históricos y archivos `.log` omitidos de Git. Restaure los archivos en las rutas documentadas por `changes/historical-sha256.json`, sin sobrescribir ni modificar contratos o archivos históricos ya presentes. El manifiesto define exactamente los bytes esperados. Sin esos binarios, la comprobación completa de integridad no puede repetirse desde un clon aislado.

`independent_oracle.py` lee el Excel directamente y calcula sus propios resultados; no usa las métricas ni banderas de FORGE/NEXUS. `browser_audit_v1.2.cjs` compara DOM real para las 160 combinaciones, 32 regresiones v1.1, restablecimiento, anomalías, fechas y móvil. Las observaciones completas están en `execution_v1.2.json`; las capturas fueron inspeccionadas visualmente.

`precision_v1.2.cjs` registra diferencias de representación IEEE cruda respecto a Python, separadas de la igualdad de valores mostrados. Son la observación histórica no bloqueante QA-002; no representan una tolerancia contractual nueva.

El informe emitido `reports/QA_REPORT_v1.2.json` es inmutable una vez consumido. `emit_report_v1.2.py` se conserva como evidencia de generación, no debe reejecutarse para sustituirlo; cualquier auditoría posterior debe emitir una nueva versión.
