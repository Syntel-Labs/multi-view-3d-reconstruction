# Referencia de geometria 3D para el pipeline SfM

Documento de lectura para la implementacion de `geometry.py`, `triangulation.py`, `sfm.py` y `metrics.py`.

Publico: estudiante con conocimientos de SIFT, homografias y matrices de camara basicas. Sin bundle adjustment.

Referencia principal: Hartley & Zisserman, *Multiple View Geometry in Computer Vision*, 2a edicion (Cambridge, 2003) — el texto en el que se basa el nombre del servicio `mv3d-hartley`.

## 1. Matriz fundamental F

### Definicion y restriccion epipolar

La matriz fundamental F es una relacion geometrica de rango 2 que vincula puntos correspondientes en dos imagenes de la misma escena:

$$\mathbf{x}'^T \mathbf{F} \mathbf{x} = 0$$

donde $\mathbf{x} = [u, v, 1]^T$ y $\mathbf{x}' = [u', v', 1]^T$ son puntos en coordenadas homogeneas.

Intuicion geometrica: el producto $\mathbf{F}\mathbf{x}$ genera la linea epipolar en la segunda imagen sobre la que debe caer $\mathbf{x}'$. La restriccion reduce la busqueda de correspondencias de 2D a 1D.

### Algoritmo de 8 puntos (Hartley, 1997)

Expandiendo la restriccion epipolar para cada par $(x_i, x'_i)$ se obtiene el sistema lineal homogeneo:

$$\mathbf{A}\mathbf{f} = 0, \quad \mathbf{A} \in \mathbb{R}^{n \times 9}$$

La solucion es el vector singular correspondiente al menor valor singular de A (ultima columna de V en la SVD de A).

**Normalizacion de Hartley (paso critico)**: sin normalizar, las coordenadas en pixeles (0-1000) generan inestabilidad numerica severa.

1. Trasladar el centroide al origen: $\bar{\mathbf{x}} = \mathbf{x} - \mathbf{c}$
2. Escalar la distancia media a $\sqrt{2}$: escala $= \sqrt{2} \,/\, \text{mean}(|\bar{\mathbf{x}}_i|)$
3. La transformacion se representa como matriz $T$ de $3 \times 3$
4. Tras resolver, deshacer: $\mathbf{F} = \mathbf{T}'^{-T} \mathbf{F}_{norm} \mathbf{T}^{-1}$

La normalizacion mejora la estabilidad numerica entre 10 y 100 veces. OpenCV la aplica internamente cuando se usa `FM_RANSAC`.

### RANSAC para robustez ante outliers

1. Muestrear aleatoriamente 8 pares
2. Calcular F candidata con el algoritmo normalizado
3. Contar inliers: punto $i$ es inlier si $\text{dist}(\mathbf{x}'_i, \mathbf{F}\mathbf{x}_i) < \tau$
4. Conservar F con maximo de inliers
5. Refinar F sobre todos los inliers

### Parametros en OpenCV

```python
F, mask = cv2.findFundamentalMat(
    points1, points2,
    method=cv2.FM_RANSAC,
    ransacReprojThreshold=1.0,   # pixeles; rango tipico 1.0 - 3.0
    confidence=0.99,
)
```

| Parametro | Rango | Recomendacion |
| :--- | :--- | :--- |
| `ransacReprojThreshold` | 0.5 - 5.0 px | 1.0 para imagenes limpias, 3.0 si hay distorsion |
| `confidence` | 0.9 - 0.999 | 0.99 es el estandar |

`mask` es un vector booleano que marca los inliers. Verificar siempre que `np.sum(mask) / len(mask) >= 0.6`.

### Errores comunes

- No normalizar puntos cuando se implementa el algoritmo manualmente
- Threshold RANSAC demasiado pequeno (rechaza inliers) o demasiado grande (acepta outliers)
- Invertir el orden de argumentos: `points1` debe pertenecer siempre a la imagen 1
- No verificar `rank(F) == 2` con SVD

### Referencias

- H&Z Capitulo 9: *Epipolar Geometry and the Fundamental Matrix* (pags. 239-261)
- [OpenCV: Tutorial Epipolar Geometry](https://docs.opencv.org/4.x/da/de9/tutorial_py_epipolar_geometry.html)
- [OpenCV: findFundamentalMat](https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html#gae420abc34eaa03d0c6a67359609d8429)
- Hartley, R. (1997). *In Defence of the 8-Point Algorithm*. IEEE TPAMI.

## 2. Matriz esencial E y descomposicion en R, t

### Relacion con F

La matriz esencial es el equivalente calibrado de F:

$$\mathbf{E} = \mathbf{K}^T \mathbf{F} \mathbf{K}$$

Propiedades de E:

- Rango exactamente 2
- Los dos valores singulares no nulos son iguales: $\sigma_1 = \sigma_2$, $\sigma_3 = 0$
- Se puede escribir como $\mathbf{E} = [\mathbf{t}]_\times \mathbf{R}$

### Descomposicion SVD en cuatro soluciones de pose

Dado $\mathbf{E} = \mathbf{U} \mathbf{\Sigma} \mathbf{V}^T$, con $\mathbf{W} = \begin{bmatrix} 0 & -1 & 0 \\ 1 & 0 & 0 \\ 0 & 0 & 1 \end{bmatrix}$:

$$\mathbf{R}_1 = \mathbf{U} \mathbf{W} \mathbf{V}^T, \quad \mathbf{R}_2 = \mathbf{U} \mathbf{W}^T \mathbf{V}^T$$
$$\mathbf{t}_1 = +\mathbf{U}_{:,2}, \quad \mathbf{t}_2 = -\mathbf{U}_{:,2}$$

Esto produce 4 configuraciones de pose: $(R_1, t_1)$, $(R_1, t_2)$, $(R_2, t_1)$, $(R_2, t_2)$.

### Restriccion de chirality (resolucion de ambiguedad)

Solo una de las 4 configuraciones produce puntos 3D *adelante de ambas camaras*. Para cada punto X triangulado y centro de camara C:

$$\mathbf{r}_3 \cdot (\mathbf{X} - \mathbf{C}) > 0$$

donde $\mathbf{r}_3$ es la tercera fila de R. La configuracion correcta es aquella que maximiza el numero de puntos que satisfacen esta condicion en ambas camaras. `cv2.recoverPose` aplica este criterio automaticamente.

### Parametros en OpenCV

```python
# Estima E con el algoritmo de 5 puntos de Nister
E, mask_E = cv2.findEssentialMat(
    points1, points2,
    cameraMatrix=K,
    method=cv2.RANSAC,
    prob=0.999,
    threshold=1.0,
)

# Descompone E, aplica chirality y devuelve la pose correcta
num_inliers, R, t, mask_pose = cv2.recoverPose(
    E, points1, points2,
    cameraMatrix=K,
    mask=mask_E,
)
```

La traslacion `t` devuelta por `recoverPose` es un vector unitario: $|\mathbf{t}| = 1$. La escala metrica es indeterminada y se recupera mediante triangulacion.

### Errores comunes

- Pasar F en lugar de E a `recoverPose`
- Usar una K incorrecta o aproximada sin documentarlo como limitacion
- Ignorar que la traslacion es unitaria al construir P2
- No verificar `rank(E) == 2` tras calcularla

### Referencias

- H&Z Capitulo 9.6: *The Essential Matrix*, y Capitulo 10: *3D Reconstruction of Cameras and Structure*
- [OpenCV: recoverPose](https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html#gadb7d2dfcc184c1d2f496d8639f4371c0)
- [CMU CMSC426: Structure from Motion](https://cmsc426.github.io/sfm/)

## 3. Triangulacion DLT

### Formulacion del problema

Dadas dos matrices de proyeccion $\mathbf{P}_1$, $\mathbf{P}_2$ y correspondencias 2D $\mathbf{x}_1$, $\mathbf{x}_2$, encontrar el punto 3D $\mathbf{X} = [X, Y, Z, 1]^T$ tal que:

$$\lambda_1 \mathbf{x}_1 = \mathbf{P}_1 \mathbf{X}, \quad \lambda_2 \mathbf{x}_2 = \mathbf{P}_2 \mathbf{X}$$

### Eliminacion del factor de escala via producto cruz

Usando $\mathbf{x} \times (\mathbf{P}\mathbf{X}) = 0$ para eliminar $\lambda$ se construye un sistema sobredeterminado de 4 ecuaciones lineales en 4 incognitas. La solucion es el vector singular de menor valor singular de la matriz $\mathbf{A}$ (ultima columna de V en la SVD):

$$\mathbf{A}\mathbf{X} = 0 \implies \mathbf{X} = \mathbf{V}_{:,3}$$

Desnormalizar de coordenadas homogeneas:

$$\mathbf{X}_{cart} = \mathbf{X}_{homo}[0:3] \;/\; \mathbf{X}_{homo}[3]$$

### Uso en OpenCV

```python
# Construir matrices de proyeccion
P1 = K @ np.hstack([np.eye(3), np.zeros((3, 1))])
P2 = K @ np.hstack([R, t.reshape(3, 1)])

# Destiorzionar puntos ANTES de triangular (paso critico)
pts1_u = cv2.undistortPoints(points1, K, dist_coeffs, P=K)
pts2_u = cv2.undistortPoints(points2, K, dist_coeffs, P=K)

# Triangular: devuelve (4, n) en coordenadas homogeneas
pts4d = cv2.triangulatePoints(P1, P2, pts1_u, pts2_u)

# Convertir a cartesianas (3, n)
pts3d = (pts4d[:3] / pts4d[3]).T
```

### Filtrar puntos invalidos

```python
# Descartar puntos detras de alguna camara (Z < 0)
R2, t2 = R, t.reshape(3)
pts_cam2 = (R2 @ pts3d.T).T + t2
validos = (pts3d[:, 2] > 0) & (pts_cam2[:, 2] > 0)
pts3d = pts3d[validos]
```

### Errores comunes

- Pasar puntos distorsionados (sin undistort) a `triangulatePoints`
- No desnormalizar las coordenadas homogeneas (dividir por w)
- Matrices P en formato incorrecto (deben ser $3 \times 4$)
- No filtrar puntos con profundidad negativa

### Referencias

- H&Z Capitulo 12.2: *Triangulation*
- [OpenCV: triangulatePoints](https://docs.opencv.org/4.x/d0/dbd/group__triangulation.html)
- [DLT explicado con codigo (Temugeb)](https://temugeb.github.io/computer_vision/2021/02/06/direct-linear-transorms.html)

## 4. SfM incremental multi-vista

### Esquema del pipeline

```bash
Entrada: secuencia de N imagenes + K
    |
    v
1. Extraer keypoints y descriptores (SIFT) en todas las imagenes
    |
    v
2. Inicializar con el mejor par (mayor inliers):
   findEssentialMat + recoverPose + triangulatePoints
    |
    v
3. Para cada nueva imagen i (i = 2 ... N-1):
   a. Matching imagen i contra la nube 3D actual
   b. solvePnPRansac -> R_i, t_i
   c. triangulatePoints con camara anterior -> nuevos puntos 3D
   d. Fusionar con la nube existente
    |
    v
Salida: cloud.ply + metrics.json
```

### Inicializacion del primer par

```python
# Seleccionar par con mayor numero de inliers de F
E, mask = cv2.findEssentialMat(pts1, pts2, K, cv2.RANSAC, 0.999, 1.0)
_, R, t, _ = cv2.recoverPose(E, pts1, pts2, K, mask=mask)

P1 = K @ np.hstack([np.eye(3), np.zeros((3, 1))])
P2 = K @ np.hstack([R, t])
pts4d = cv2.triangulatePoints(P1, P2, pts1_u, pts2_u)
pts3d = (pts4d[:3] / pts4d[3]).T
```

### Registro incremental con solvePnPRansac

```python
success, rvec, tvec, inliers = cv2.solvePnPRansac(
    objectPoints=world_pts.astype(np.float64),   # puntos 3D de la nube
    imagePoints=image_pts.astype(np.float64),    # correspondencias en imagen i
    cameraMatrix=K,
    distCoeffs=None,
    reprojectionError=8.0,
    confidence=0.99,
    iterationsCount=100,
    flags=cv2.SOLVEPNP_EPNP,
)
if success and len(inliers) >= 10:
    R_i, _ = cv2.Rodrigues(rvec)
```

| Parametro | Valor tipico | Impacto |
| :--- | :--- | :--- |
| `reprojectionError` | 8.0 px | Umbral de inlier para RANSAC interno |
| `confidence` | 0.99 | Mas alto = mas iteraciones |
| `iterationsCount` | 100 | Incrementar a 300 si hay mucho ruido |
| `flags` | `SOLVEPNP_EPNP` | O(n) lineal, buena precision |

### Condicion de rechazo de una nueva vista

Si `success == False` o `len(inliers) < 10` o el error de reproyeccion medio supera 2 px, descartar la imagen y continuar.

### Errores comunes en el pipeline incremental

- No filtrar outliers de matching antes de solvePnPRansac
- Usar coordenadas distorsionadas en solvePnPRansac
- Aceptar puntos con Z < 0 (detras de la camara)
- No validar el exito de RANSAC antes de agregar la vista
- Acumular drift sin detectarlo (monitorear RMSE en cada paso)

### Referencias

- H&Z Capitulo 10: *3D Reconstruction of Cameras and Structure*
- [OpenCV Blog: Structure from Motion](https://opencv.org/blog/structure-from-motion-in-opencv/)
- [OpenCV: solvePnPRansac](https://docs.opencv.org/4.x/d5/d1f/calib3d_solvePnP.html)
- [Pipeline completo de referencia (CMU)](https://cmsc426.github.io/sfm/)

## 5. Error de reproyeccion

### Definicion

Para un punto 3D $\mathbf{X}$ observado en la imagen $i$ como $\mathbf{x}_{obs}$, el error de reproyeccion es:

$$e_i = \|\mathbf{x}_{obs,i} - \pi(\mathbf{P}\mathbf{X})\|_2$$

donde $\pi$ es la proyeccion perspectiva (division por z).

El RMSE sobre $n$ puntos:

$$\text{RMSE} = \sqrt{\frac{1}{n}\sum_{i=1}^n e_i^2}$$

### Interpretacion practica

| RMSE | Calidad |
| :--- | :--- |
| < 1.0 px | Excelente |
| 1.0 - 2.0 px | Buena (objetivo del proyecto) |
| 2.0 - 5.0 px | Mediocre, revisar K o matches |
| > 5.0 px | Deficiente |

### Implementacion

```python
def reprojection_error(pts3d, pts2d_obs, K, R, t):
    """pts3d: (n,3), pts2d_obs: (n,2). Devuelve errores por punto y RMSE."""
    P = K @ np.hstack([R, t.reshape(3, 1)])
    pts_h = np.hstack([pts3d, np.ones((len(pts3d), 1))]).T  # (4, n)
    proj = P @ pts_h                                          # (3, n)
    proj = (proj[:2] / proj[2]).T                            # (n, 2)
    errors = np.linalg.norm(pts2d_obs - proj, axis=1)
    return errors, float(np.sqrt(np.mean(errors**2)))
```

### Diagnostico de RMSE alto

- K incorrecta o aproximada: revisar focal length y punto principal
- Distorsion de lente no corregida: aplicar undistort antes de usar los puntos
- Correspondencias incorrectas: visualizar matches, ajustar ratio test de Lowe
- Pose mal estimada: aumentar `iterationsCount` en solvePnPRansac
- Drift acumulado: limitacion conocida del SfM incremental sin bundle adjustment (documentar en la Conclusion)

### Referencias

- H&Z Capitulo 12: *Bundle Adjustment* (contexto del error de reproyeccion como funcion de costo)
- [What is Reprojection Error (TrueGeometry)](https://blog.truegeometry.com/api/exploreHTML/1efabfdc22c99560ede2436b790a4a82.exploreHTML)

## 6. Matriz intrinseca K desde EXIF

### Formulacion

$$\mathbf{K} = \begin{bmatrix} f_x & 0 & c_x \\ 0 & f_y & c_y \\ 0 & 0 & 1 \end{bmatrix}$$

Relacion entre focal en mm y focal en pixeles:

$$f_x = f_{mm} \cdot \frac{w_{px}}{w_{sensor\,mm}}, \quad f_y = f_{mm} \cdot \frac{h_{px}}{h_{sensor\,mm}}$$

El punto principal se asume en el centro: $c_x = w/2$, $c_y = h/2$.

### Formula alternativa con focal en 35mm equivalente

Si el EXIF solo provee `FocalLengthIn35mmFilm`:

$$f_x \approx f_{35mm} \cdot \frac{w_{px}}{36}$$

ya que el sensor de referencia 35 mm mide 36 x 24 mm.

### Extraccion desde EXIF con exifread

```python
import exifread

def focal_mm_from_exif(path: str) -> float | None:
    with open(path, "rb") as f:
        tags = exifread.process_file(f, stop_tag="EXIF FocalLength", details=False)
    tag = tags.get("EXIF FocalLength")
    if tag is None:
        return None
    val = tag.values[0]          # IFDRational
    return float(val.num) / float(val.den)
```

### Tamanhos de sensor tipicos

| Dispositivo | Ancho sensor (mm) | Alto sensor (mm) |
| :--- | :--- | :--- |
| iPhone 12 / 13 (gran angular) | 4.636 | 3.480 |
| iPhone 15 Pro (gran angular) | 4.800 | 3.600 |
| Pixel 5 / 7 (principal) | 4.410 | 3.307 |
| Samsung Galaxy S21+ | 4.410 | 3.307 |
| Sensor 1/2.3" (generico) | 6.160 | 4.620 |
| Sensor 1/1.7" (generico) | 7.600 | 5.700 |

### Validacion de K

```python
def validate_K(K, w, h):
    fx, fy = K[0, 0], K[1, 1]
    cx, cy = K[0, 2], K[1, 2]
    fov_x = 2 * np.degrees(np.arctan(w / (2 * fx)))
    assert 20 < fov_x < 120, f"FOV horizontal fuera de rango: {fov_x:.1f}°"
    assert abs(cx - w / 2) < 0.2 * w, "Punto principal desviado"
    assert fx > 0 and fy > 0
```

Valores esperados para un telefono tipico con imagen 4032 x 3024: $f_x \approx 3000$-$4000$ px, FOV horizontal entre 60° y 80°.

### Limitacion conocida

Sin tablero de calibracion, K se aproxima desde EXIF. Los efectos de distorsion radial no se modelan. Documentar como limitacion en la seccion de Conclusion del documento final.

### Referencias

- [Dissecting the Camera Matrix - Intrinsics (ksimek)](https://ksimek.github.io/2013/08/13/intrinsic/)
- [OpenCV: Camera Calibration Tutorial](https://docs.opencv.org/4.x/dc/dbb/tutorial_py_calibration.html)
- `exifread` ya esta en `requirements.txt` del proyecto

## Resumen de decisiones de implementacion

| Modulo | Funcion OpenCV clave | Parametro critico | Referencia H&Z |
| :--- | :--- | :--- | :--- |
| `geometry.py` | `findFundamentalMat(FM_RANSAC)` | `ransacReprojThreshold=1.0` | Cap. 9 |
| `geometry.py` | `findEssentialMat` + `recoverPose` | `threshold=1.0` | Cap. 9.6 |
| `triangulation.py` | `triangulatePoints` | undistort previo | Cap. 12.2 |
| `sfm.py` | `solvePnPRansac(SOLVEPNP_EPNP)` | `reprojectionError=8.0` | Cap. 10 |
| `metrics.py` | proyeccion manual | RMSE objetivo < 2 px | Cap. 12 |
| `config.py` | `exifread` | tabla de sensores | — |
