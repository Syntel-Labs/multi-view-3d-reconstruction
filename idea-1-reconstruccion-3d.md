# Idea 1 — Reconstrucción 3D desde Múltiples Fotografías (Structure from Motion)

## Descripción del problema

Dado un conjunto de fotografías de un objeto o escena tomadas desde distintos ángulos, reconstruir su geometría 3D de forma automática sin equipamiento especializado. Aplicación real en arqueología, arquitectura, videojuegos, e-commerce y manufactura.

## Pipeline core

```bash
Fotos → Detección de keypoints (SIFT/ORB) → Matching → RANSAC
      → Estimación de matriz fundamental → Triangulación → Nube de puntos 3D
```

## Temas del curso ya vistos

| Tema | Semana | Uso en el proyecto |
| :--- | :--- | :--- |
| SIFT / ORB | 4 | Detectar puntos de interés en cada imagen |
| RANSAC | 4 | Filtrar correspondencias incorrectas |
| Geometría proyectiva | 5 | Modelo pinhole, matriz fundamental y esencial |
| Homografías | 5-6 | Estimación de poses de cámara relativas |
| Filtrado y convolución | 2 | Preprocesamiento de imágenes de entrada |
| Morfología matemática | 3 | Limpieza de fondo antes del matching |

### Matemática central

La proyección de un punto 3D $X = (X, Y, Z, 1)^T$ al plano imagen se modela como:

$$
\lambda \begin{bmatrix} u \\ v \\ 1 \end{bmatrix} = K [R \mid t] \begin{bmatrix} X \\ Y \\ Z \\ 1 \end{bmatrix}
$$

donde $K$ es la matriz intrínseca, $R$ y $t$ son los parámetros extrínsecos y $\lambda$ es el factor de escala.

La relación entre correspondencias en dos imágenes se expresa mediante la matriz fundamental $F$:

$$
x'^T F x = 0
$$

El error de reproyección que se minimiza es:

$$
E = \sum_i \| x_i - \hat{x}(P, X_i) \|^2
$$

## Extras integrables (no core — temas por venir)

| Tema | Semana | Adición |
| :--- | :--- | :--- |
| Segmentación | 14 | Separar objeto de fondo automáticamente antes de la reconstrucción |
| Transformers en Visión (ViT) | 15 | Usar SuperGlue o LightGlue como comparativa vs SIFT clásico |
| Modelos Generativos | 17-18 | Comparar con NeRF o Gaussian Splatting como marco teórico |

## Métricas demostrables

| Métrica | Descripción | Objetivo |
| :--- | :--- | :--- |
| Reprojection Error | $\|x_i - \hat{x}(P, X_i)\|$ en píxeles | $< 2$ px |
| Inliers RANSAC | Porcentaje de correspondencias válidas | $> 60\%$ |
| Densidad de nube | Puntos reconstruidos vs. puntos intentados | Maximizar |
| Tiempo de procesamiento | Por imagen y total del pipeline | Documentar |
| Cobertura angular | Mínimo de ángulos para calidad aceptable | Evaluar |

## Demo web

```bash
Usuario sube N fotos
  → backend corre pipeline SfM con OpenCV
  → genera archivo .ply / .obj
  → Three.js visualiza nube 3D interactiva en el navegador
  → panel lateral muestra métricas en tiempo real
```

Funcionalidades de la demo:

- Visualización 3D rotable con zoom en el navegador
- Métricas visibles durante el procesamiento
- Comparativa opcional: SIFT clásico vs. matching moderno

## Referencias

- COLMAP — <https://colmap.github.io/> (SfM + MVS de referencia académica)
- OpenCV `sfm` module — parte de `opencv_contrib`
- Sarlin et al. (2020) — *SuperGlue: Learning Feature Matching with Graph Neural Networks*
- Lindenberger et al. (2023) — *LightGlue: Local Feature Matching at Light Speed*
- Meshroom / AliceVision — pipeline SfM open source
- Agarwal et al. (2009) — *"Reconstructing Rome"*
