# Hoja de avance 1 - CC3045 Procesamiento de Imagenes

**Fecha:** 30 de abril de 2026

**Repositorio:** <https://github.com/Syntel-Labs/multi-view-3d-reconstruction>

| Name              | Institution ID | GitHub User |
| ----------------- | -------------- | ----------- |
| Edwin de León     | 22809          | EJGDLG      |
| Gustavo Cruz      | 22779          | G2309       |
| Mathew Cordero    | 22982          | donmatthiuz |
| Josué Say         | 22801          | JosueSay    |

## Problema

Reconstruir una nube de puntos 3D a partir de un conjunto de fotografias tomadas desde distintos angulos de un mismo objeto, sin camaras calibradas ni sensores de profundidad. El resultado se visualiza en un navegador web.

## Solucion propuesta

Pipeline clasico de Structure from Motion (SfM) implementado en Python con OpenCV, expuesto mediante una API REST y visualizado con Three.js:

1. Preprocesamiento y deteccion de keypoints (SIFT / ORB)
2. Matching entre imagenes con Lowe ratio test
3. Estimacion de geometria epipolar (F, E, pose relativa)
4. Triangulacion DLT multi-vista incremental
5. Exportacion de nube de puntos `.ply` y metricas

## Pipeline

```bash
Fotos -> Preproceso -> SIFT/ORB -> BFMatcher+Lowe -> RANSAC+F -> E -> recoverPose -> DLT -> solvePnPRansac -> .ply -> Three.js
```

## Tecnologias

| Capa | Tecnologia |
| :--- | :--- |
| Vision | Python 3.12, OpenCV 4.10, NumPy |
| API | FastAPI + uvicorn |
| Frontend | Three.js 0.169, Vite 5.4, pnpm |
| Infraestructura | Docker Compose, ruff |

## Mini cronograma

| Fecha | Hito |
| :--- | :--- |
| 30 abr | Entrega 1: skeleton + features + geometria sintetica + demo mock |
| 07 may | Entrega 2: pipeline end-to-end + demo web con pipeline real |
| 21 may | Entrega final: 3 datasets + documento + slides + video |

## Estado actual

El repositorio cuenta con la estructura modular completa y el entorno Docker funcionando. La deteccion de features (SIFT/ORB) corre sobre datasets reales. El modulo de geometria epipolar estima la matriz fundamental F con 72% de inliers sobre un par sintetico controlado (criterio >= 60%). La demo web levanta con el backend respondiendo `/health` y el frontend mostrando la escena Three.js en `localhost:5175`. Los datasets se encuentran en proceso de captura.
