# Hoja de avance 2 - CC3045 Procesamiento de Imagenes

**Fecha:** 7 de mayo de 2026

**Repositorio:** <https://github.com/Syntel-Labs/multi-view-3d-reconstruction>

| Nombre            | Carne | GitHub       |
| ----------------- | ----- | ------------ |
| Edwin de Leon     | 22809 | EJGDLG       |
| Gustavo Cruz      | 22779 | G2309        |
| Mathew Cordero    | 22982 | donmatthiuz  |
| Josue Say         | 22801 | JosueSay     |

## Estado actual

El pipeline SfM corre de extremo a extremo por CLI sobre dos datasets reales y genera `cloud.ply` + `metrics.json` verificables. El backend expone los archivos via HTTP con CORS. La demo web de Persona C tiene el visor Three.js funcionando con PLY mock y el endpoint `/reconstruct`; la integracion con el pipeline real esta en curso.

## Metricas reales

| Dataset          | Imagenes | Camaras registradas | Puntos 3D | Repr. error medio | Inlier ratio |
| :--------------- | :------: | :-----------------: | :-------: | :---------------: | :----------: |
| controlgamecube  | 78       | 18                  | 403       | **0.23 px**       | 57.6 %       |
| apple\_co3d      | 102      | 12                  | 358       | **0.20 px**       | 43.7 %       |

Ambos datasets superan el criterio de calidad de la entrega (error < 2 px).

## Nube de puntos - controlgamecube

```bash
Vista lateral (proyeccion XZ)           Vista frontal (proyeccion XY)

     Z                                       Y
     ^   . . .  .                            ^  .  . .
     |  .  . . . .                           | . . . . .
     | . .  . .. .  .                        |  . . . .  .
     |  . .  .  .                            | . .  . .
     +-----------> X                         +-----------> X

     403 puntos  |  span X: 1.8 u  |  span Z: 0.9 u
```

Centrado por percentil 5-95 para ignorar outliers extremos. Visualizable en `outputs/controlgamecube/test_viewer.html`.

## Endpoints del backend

| Endpoint                              | Descripcion                     |
| :------------------------------------ | :------------------------------ |
| `GET /health`                         | Liveness probe                  |
| `GET /outputs/{dataset}/cloud.ply`    | Descarga la nube en formato PLY |
| `GET /outputs/{dataset}/metrics`      | Metricas del pipeline en JSON   |

## Checklist de avance funcional

- [x] Pipeline SfM end-to-end por CLI genera `cloud.ply` + `metrics.json`
- [x] Reprojection error medio < 2 px en ambos datasets (0.23 px y 0.20 px)
- [ ] Demo web conectada al pipeline real (Persona C — pendiente de integracion)
- [ ] Dataset 3 capturado con intrinsics completos (Persona D — imagenes pendientes)
- [ ] Documento final secciones 1 a 4 (todas las personas — pendiente)

## Bloqueos

- **Cobertura de camaras baja**: controlgamecube registra 18/78 camaras (23 %) porque el matching actual solo cubre pares consecutivos. El frame siguiente puede no solapar si el video tiene saltos. La solucion es matching en ventana ampliada (Persona A, pendiente).
- **Intrinsics del dataset Exterior**: el archivo `data/Exterior/intrinsics.json` tiene todos los campos en cero; el pipeline no puede correr sin focal length real. Persona D debe completarlo con los valores EXIF o la heuristica `f = 1.2 * max(W, H)`.
- **Documento final**: todas las secciones estan como "Pendiente" en `docs/final/document.md`.

## Pendientes para la entrega final (21 mayo)

| Persona | Tarea |
| :------ | :---- |
| A | Matching en ventana ampliada para aumentar camaras registradas; comparativa SIFT vs ORB; seccion 4.1 del documento |
| B | Secciones 4.2, 4.3, 4.4 del documento; validacion sobre datasets 2 y 3; experimentacion final |
| C | Conectar visor Three.js al pipeline real en `frontend/src/viewer/pointCloudViewer.js`; integrar en el stack Docker |
| D | Capturar dataset 3 con imagenes e intrinsics completos; redactar secciones 1, 2, 3, 5, 6, 7 del documento; slides y video |
