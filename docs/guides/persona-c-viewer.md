# Guia de integracion - Visor 3D (Persona C)

Referencia de contratos: [cloud-ply.md](../contracts/cloud-ply.md) | [metrics-json.md](../contracts/metrics-json.md)

- Implementar el visor Three.js en `frontend/src/viewer/pointCloudViewer.js`.
- Persona B implementó el backend completo.
- Tarea: consumir salidas y renderizarlas.

---

## Prerequisitos

- Docker Desktop corriendo
- El repositorio clonado en local

---

## Levantar el stack

```bash
# Desde la raiz del repositorio
docker compose up -d
```

Servicios que quedan activos:

| Servicio | Puerto | Descripcion |
|---|---|---|
| `hartley` (backend) | `localhost:8000` | API FastAPI + pipeline SfM |
| `galileo` (frontend) | `localhost:5175` | Vite dev server (tu entorno) |

Verificar que el backend responde:

```bash
curl http://localhost:8000/health
# {"status":"ok"}
```

---

## Generar la nube de puntos de un dataset

Si los archivos `outputs/<dataset>/cloud.ply` y `outputs/<dataset>/metrics.json` no existen
o quieres regenerarlos con nuevas imagenes:

```bash
make pipeline DATASET=controlgamecube
make pipeline DATASET=apple_co3d
```

Datasets disponibles actualmente:

| Nombre | Imagenes | Camaras registradas | Reprojection error |
|---|---|---|---|
| `controlgamecube` | 78 | 18 | 0.23 px |
| `apple_co3d` | 102 | 12 | 0.20 px |

---

## Endpoints del backend

### GET /outputs/{dataset}/cloud.ply

Descarga el archivo PLY de la nube de puntos.

```bash
curl http://localhost:8000/outputs/controlgamecube/cloud.ply -o cloud.ply
```

Formato: PLY ASCII con campos `x y z red green blue` por vertice.
Los colores actuales son todos `255 255 255` (blanco) — se puede asignar color por posicion Z o por imagen si quieres.

### GET /outputs/{dataset}/metrics

Devuelve las metricas del pipeline en JSON.

```bash
curl http://localhost:8000/outputs/controlgamecube/metrics
```

```json
{
  "dataset": "controlgamecube",
  "num_images": 18,
  "reprojection_error_mean": 0.2284,
  "reprojection_error_median": 0.2091,
  "ransac_inlier_ratio": 0.5761,
  "num_3d_points": 403,
  "time_per_stage_seconds": { ... }
}
```

### GET /health

Probe de liveness. Responde `{"status":"ok"}` si el backend esta vivo.

---

## Lo que se debe implementar

Archivo: `frontend/src/viewer/pointCloudViewer.js`

La funcion `initViewer(root)` ya existe como stub. Debes:

1. Crear una escena Three.js dentro del elemento `root`
2. Cargar el PLY desde `http://localhost:8000/outputs/<dataset>/cloud.ply`
3. Renderizar los puntos con `THREE.Points`
4. Agregar `OrbitControls` para rotar/zoom/pan con el mouse
5. Mostrar las metricas en un panel (opcional pero recomendado)

El dataset activo puede venir de un selector en la UI, una variable de entorno, o hardcodeado para empezar.

---

## Referencia de implementacion

Existe un visor de prueba completamente funcional que puedes usar como base:

```bash
outputs/controlgamecube/test_viewer.html
outputs/apple_co3d/test_viewer.html
```

Abrir directo en el navegador (sin servidor). Incluye:

- Carga de PLY via `PLYLoader` de Three.js
- Centrado robusto con percentil 5-95 (ignora outliers)
- `OrbitControls` con damping
- Panel de metricas conectado a la API
- Ajuste automatico de camara al span de la nube

Se puede copiar ese codigo directamente a `pointCloudViewer.js` y adaptarlo al stack del frontend.

---

## Nube de puntos vs modelo 3D solido

El pipeline implementado es SfM (Structure from Motion). La salida es una **nube de puntos dispersa**: un conjunto de puntos 3D en el espacio, uno por keypoint SIFT triangulado. No es un modelo solido con superficie ni textura.

Lo que se verá en el visor:

- Puntos flotantes en el espacio — no triangulos, no malla, no superficie
- Con un dataset de buena calidad (objeto texturado, fotos estaticas con solapamiento alto) la forma del objeto empieza a ser reconocible en la distribucion de puntos
- Con datasets de baja textura o video comprimido la nube es muy dispersa y el objeto no se distingue

Para obtener un modelo 3D solido y visible del objeto se necesitan dos etapas adicionales que estan **fuera del alcance del proyecto**:

1. **MVS (Multi-View Stereo)**: densifica la nube usando todas las imagenes simultaneamente (herramientas: COLMAP dense, OpenMVS)
2. **Reconstruccion de superficie**: convierte la nube densa en una malla de triangulos con textura (Poisson Surface Reconstruction, Marching Cubes)

Persona C no necesita implementar esas etapas. Su tarea es visualizar correctamente la nube dispersa que produce el pipeline actual.

## Notas tecnicas sobre la nube

- Los puntos estan en coordenadas del mundo con origen en la primera camara
- El eje Z apunta hacia la escena (profundidad)
- Algunos puntos pueden estar muy alejados en Z — el filtro IQR del pipeline ya elimina los peores outliers, pero el centrado por percentiles en el visor es mas robusto que usar `boundingBox`
- Con datasets de baja textura (manzana lisa, video comprimido) la nube es dispersa y no dibuja la forma del objeto — eso es una limitacion del dataset, no del pipeline
- Con fotos estaticas de buena calidad el mismo pipeline produce nubes densas y reconocibles

---

## Comandos rapidos de referencia

```bash
# Levantar stack
docker compose up -d

# Regenerar nube de un dataset
make pipeline DATASET=controlgamecube

# Ver logs del backend
make logs-backend

# Verificar endpoints
curl http://localhost:8000/health
curl http://localhost:8000/outputs/controlgamecube/metrics
```
