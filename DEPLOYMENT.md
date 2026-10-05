# Publicación GitHub Pages — preparación v1.3

La funcionalidad sigue siendo v1.2. `docs/index.html` es una copia exacta de `src/v1.2/dashboard.html` en main cbf7c25c72e9f2bf14bbe978cc70e7de36050b0e. No hay build, backend ni dependencias web externas. Solo se publicará docs; el historial y contratos quedan fuera del directorio servido.

PROJECT_SPEC pasa de 1.1 a 1.2 por el alcance de publicación y sus aprobaciones; DATA_SPEC permanece 1.1; DEV_REPORT y QA_REPORT pasan a 1.3. Las versiones anteriores y src/v1.2 permanecen intactos.

## Pasos pendientes, después de revisar y aprobar el PR

1. Fusionar el PR hacia main únicamente con aprobación del usuario.
2. En el repositorio: Settings → Pages → Build and deployment → Source: Deploy from a branch → Branch: main → Folder: /docs → Save. Este paso activa la publicación y requiere aprobación posterior.
3. Esperar el proceso de Pages y comprobar la URL que GitHub informe. URL esperada, todavía no publicada ni verificada: https://rodrigokcres.github.io/atlas-servicenow-dashboard-lab/
4. Abrir la URL y comprobar filtros combinados, restablecimiento, indicadores y vista móvil. Registrar esta validación real después de publicar.

El repositorio contiene datos sintéticos según README; el HTML publica exactamente esos datos embebidos. Si GitHub bloquea Pages por visibilidad o plan, registrar el bloqueo y decidir con el usuario, sin cambiar automáticamente la visibilidad. No se agrega workflow de despliegue.

## Comprobación local

`python3 -m http.server 8000 --directory docs` y abrir http://localhost:8000/.

Para futuras actualizaciones autorizadas, copiar nuevamente el HTML validado a docs/index.html y repetir QA; no editar manualmente dos implementaciones divergentes.
