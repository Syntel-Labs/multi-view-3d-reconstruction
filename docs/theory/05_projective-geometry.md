# Visión por Computadora – Semana 5 – Geometría Proyectiva, Modelo de Cámara y Alineación

## 1. Contexto: ¿Dónde estamos en el pipeline?

Hasta ahora:

- **Semana 1:** Imagen = tensor numérico. Preprocesamiento, color, histogramas.
- **Semana 2:** Convolución, gradientes, Canny.
- **Semana 3:** Fourier y morfología.
- **Semana 4:** Características locales (Harris, SIFT, ORB, matching, RANSAC).

Ahora damos el salto clave:

> Pasar de detectar puntos en imágenes a entender cómo se relacionan geométricamente en 3D.

## 2. El problema central

Queremos:

- Mapear puntos clave de una imagen A a una imagen B.
- Alinear imágenes.
- Entender cómo un objeto 3D se convierte en una imagen 2D.
- Resolver correspondencias robustas (RANSAC).

Pero hay un problema fundamental:

> El mundo es 3D.
> El sensor de la cámara es 2D.

Necesitamos un marco matemático que explique esa proyección.

## 3. ¿Por qué la distancia euclidiana no es suficiente?

En geometría clásica:

- Líneas paralelas nunca se cruzan.
- La distancia es fija y absoluta.

En imágenes reales:

- Las vías del tren parecen converger.
- Las carreteras se “cierran” en el horizonte.
- Objetos se hacen más pequeños con la distancia.

Esto rompe la intuición euclidiana.

La distancia euclidiana falla cuando:

- Los puntos tienden al infinito.
- Existen puntos de fuga.
- Hay perspectiva.

Por eso usamos **Geometría Proyectiva**.

## 4. Espacio Proyectivo y Coordenadas Homogéneas

### 4.1 Punto euclidiano

Un punto tradicional:

$$

(x, y) \in \mathbb{R}^2
$$

Pero esto no puede representar el infinito.

### 4.2 Punto homogéneo

Se añade una dimensión:

$$
(x, y) \rightarrow (x, y, w)
$$

donde:

- $w$ es un **factor de escala**
- El punto real se recupera como:

$$
\left(\frac{x}{w}, \frac{y}{w}\right)
$$

### 4.3 Equivalencia de escala

$$
(1,2,1) \equiv (2,4,2)
$$

Ambos representan el mismo punto porque:

$$
\left(\frac{1}{1}, \frac{2}{1}\right)
=====================================

\left(\frac{2}{2}, \frac{4}{2}\right)
$$

Esto introduce:

> Invariancia a escala

### 4.4 Punto en el infinito

Cuando:

$$
w = 0
$$

tenemos un punto ideal (en el infinito).

Ejemplo:

$$
(1,0,0)
$$

Representa un punto en el infinito en dirección del eje x.

Esto modela matemáticamente:

- Puntos de fuga
- Convergencia de paralelas

## 5. ¿Por qué usamos coordenadas homogéneas?

Porque permiten:

1. Representar el infinito.
2. Convertir divisiones en multiplicaciones matriciales.
3. Representar rotaciones y traslaciones como matrices.

Sin ellas:

- Las traslaciones no serían lineales.
- La proyección no sería expresable como producto matricial.

## 6. Modelo de Cámara Pinhole (Cámara Estenopeica)

### 6.1 Intuición física

- La luz pasa por un pequeño agujero.
- Se proyecta invertida en el sensor.
- Se forman triángulos semejantes.

### 6.2 Relación geométrica

Si:

- $X$ = coordenada real
- $Z$ = profundidad
- $f$ = distancia focal
- $x$ = coordenada en imagen

Entonces:

$$
\frac{X}{Z} = -\frac{x}{f}
$$

Despejando:

$$
x = -f \frac{X}{Z}
$$

El signo negativo indica inversión.

### 6.3 Interpretación humana

- Objetos más lejos → más pequeños.
- La escala depende de $\frac{1}{Z}$.
- La imagen es una proyección.

## 7. De 3D a 2D con matrices

En coordenadas homogéneas:

$$
\mathbf{x} = K [R | T] \mathbf{X}
$$

donde:

- $\mathbf{X}$ = punto 3D homogéneo
- $R$ = rotación
- $T$ = traslación
- $K$ = intrínsecos
- $\mathbf{x}$ = punto imagen homogéneo

## 8. Parámetros Intrínsecos (Matriz K)

$$
K =
\begin{bmatrix}
f_x & s & c_x \
0 & f_y & c_y \
0 & 0 & 1
\end{bmatrix}
$$

### Componentes

- $f_x, f_y$: distancia focal en píxeles
- $s$: skew (≈ 0 en cámaras modernas)
- $c_x, c_y$: centro óptico

### Interpretación humana

Es el “ADN” interno de la cámara.

Describe:

- Escala
- Centro de proyección
- Deformaciones internas

## 9. Parámetros Extrínsecos (R y T)

- $R$: matriz 3x3 de rotación
- $T$: vector 3x1 de traslación

Representan:

> Dónde está la cámara en el mundo.

Tienen 6 grados de libertad:

- 3 rotación
- 3 traslación

Si la cámara está alineada con el mundo:

$$
R = I, \quad T = 0
$$

## 10. Matriz de Proyección

$$
P = K [R | T]
$$

Mapea:

$$
\text{Mundo 3D homogéneo} \rightarrow \text{Imagen 2D homogénea}
$$

La cámara no es una caja negra.

Es una transformación lineal.

## 11. Transformaciones Proyectivas en 3D y 2D

### 11.1 Transformaciones en 3D (Movimiento de Cuerpo Rígido)

Antes de hablar de homografías, recordemos lo que ocurre en 3D.

Un punto del mundo $\mathbf{X}$ se proyecta como:

$$
\mathbf{x} = K [R|t] \mathbf{X}
$$

Primero se aplica la **transformación extrínseca**:

$$
\mathbf{X}_{cam} = R\mathbf{X} + t
$$

Esto representa un **movimiento de cuerpo rígido**:

- Rotación (R) (3 GDL)
- Traslación (t) (3 GDL)

Total: **6 grados de libertad**

Este movimiento:

- No deforma el objeto.
- Conserva distancias en el espacio 3D.
- Solo cambia su posición y orientación.

Después se aplica la **matriz intrínseca (K)**, que convierte coordenadas de cámara en píxeles.

Flujo completo (como en la diapositiva de flujo de coordenadas ):

$$
P_{pixel} = K \cdot [R|t] \cdot P_{mundo}
$$

### 11.2 Transformaciones Proyectivas en el Plano 2D

Ahora trabajamos directamente en el plano imagen → plano imagen.

Aquí usamos **coordenadas homogéneas**:

$$
(x, y) \rightarrow (x, y, 1)
$$

Una transformación proyectiva se escribe:

$$
\mathbf{x'} = H\mathbf{x}
$$

donde (H) es una matriz 3×3 no singular.

## 12. Grados de Libertad y Tipos de Transformaciones

Un **grado de libertad (GDL)** es un parámetro independiente que puede ajustarse.

En 2D:

### 12.1 Isometría (3 GDL)

- Traslación en X
- Traslación en Y
- Rotación

Mantiene:

- Forma
- Tamaño
- Ángulos

Es transformación rígida.

### 12.2 Similitud (4 GDL)

Isometría + escala isotrópica.

Permite:

- Cambiar tamaño uniformemente.

Ejemplo: Redimensionar manteniendo proporciones (como mantener SHIFT).

### 12.3 Afín (6 GDL)

Similitud + 2 parámetros adicionales.

Permite:

- Escalar distinto en X y Y
- Inclinación (skew)

Mantiene:

- Líneas paralelas como paralelas.

Permite “enderezar” ciertas imágenes.

### 12.4 Proyectiva / Homografía (8 GDL)

Es la transformación lineal más general en el plano proyectivo .

Permite:

- Que paralelas converjan (puntos de fuga)
- Estirar bordes de forma desigual
- Simular perspectiva

Mantiene:

- Colinealidad (líneas rectas siguen siendo rectas)

Se representa como:

$$
H =
\begin{bmatrix}
h_{11} & h_{12} & h_{13} \
h_{21} & h_{22} & h_{23} \
h_{31} & h_{32} & h_{33}
\end{bmatrix}
$$

## 13. ¿Por qué 8 Grados de Libertad y no 9?

La matriz (H) tiene 9 parámetros.

Pero en geometría proyectiva:

$$
\mathbf{x} \sim \lambda \mathbf{x}
$$

Multiplicar toda la matriz por un escalar no cambia el resultado final, porque al final dividimos por la última coordenada.

Entonces:

- 9 parámetros
- 1 escala global ambigua

Resultado: **8 grados de libertad reales**

Ese parámetro perdido es el “grado sacrificado por ambigüedad de escala”.

## 14. ¿Por qué necesitamos 4 puntos?

Cada punto en el plano aporta:

$$
(x, y) \Rightarrow 2 ecuaciones
$$

Si tenemos 8 incógnitas independientes:

$$
4 puntos \times 2 ecuaciones = 8 ecuaciones
$$

Por eso el mínimo para estimar una homografía es **4 correspondencias** .

## 15. DLT (Direct Linear Transformation)

Queremos encontrar (H) tal que:

$$
\mathbf{x'}_i \times H\mathbf{x}_i = 0
$$

Esto genera un sistema lineal homogéneo:

$$
A\mathbf{h} = 0
$$

donde:

- (A) es matriz $2N \times 9$
- $\mathbf{h}$ es el vector con los 9 parámetros de (H)

Problema:

La solución trivial es:

$$
\mathbf{h} = 0
$$

Pero eso no sirve (sería transformación nula).

Entonces agregamos restricción:

$$
|\mathbf{h}| = 1
$$

Y buscamos:

$$
\min |A\mathbf{h}| \quad \text{sujeto a} \quad |\mathbf{h}| = 1
$$

## 16. Resolución con SVD

Usamos:

$$
A = U \Sigma V^T
$$

Interpretación geométrica (como en la diapositiva de la elipse ):

1. $V^T$: rotación en espacio de entrada
2. $\Sigma$: escalamiento
3. $U$: rotación en espacio de salida

La solución óptima de (A\mathbf{h}=0) es:

> El vector singular derecho asociado al menor valor singular.

Es decir:

$$
\mathbf{h} = \text{última columna de } V
$$

Porque esa dirección es la que:

$$
A\mathbf{h}
$$

“aplana” más el sistema (error mínimo en mínimos cuadrados).

## 17. Pseudoinversa y Mínimos Cuadrados

En problemas no homogéneos:

$$
Ax = b
$$

Se usa pseudoinversa:

$$
x = A^+ b = V\Sigma^{-1}U^T b
$$

Pero en homografía trabajamos con sistema homogéneo, por eso usamos el menor valor singular.

## 18. Normalización de Datos (Regla de Oro)

SVD es numéricamente inestable si los datos no están normalizados .

Proceso (Hartley):

1. Trasladar centroides al origen
2. Escalar para que distancia promedio sea $\sqrt{2}$
3. Calcular SVD
4. Desnormalizar:

$$
H_{final} = T'^{-1} H T
$$

Sin esto:

- Los valores pueden explotar.
- La solución se vuelve inestable.

## 19. Problema de Outliers

Cuando hacemos:

- SIFT
- ORB
- Harris
- Matching de descriptores

Obtenemos correspondencias incorrectas.

DLT asume ruido Gaussiano.
Pero un solo outlier puede destruir la solución .

Mínimos cuadrados:

- Penaliza mucho errores grandes.
- El modelo “se dobla” para acomodar errores extremos.
- No es robusto.

No podemos filtrar por distancia antes de calcular H,
porque la distancia depende de H.

Problema del huevo y la gallina.

## 20. RANSAC (Random Sample Consensus)

Solución robusta basada en consenso, no promedio .

### Algoritmo

1. Seleccionar (s=4) puntos aleatorios.
2. Calcular (H_{test}).
3. Contar inliers:

$$
|\mathbf{x'} - H_{test}\mathbf{x}| < \text{umbral}
$$

4. Repetir N veces.
5. Elegir modelo con más inliers.
6. Refinar con todos los inliers usando SVD final.

## 21. ¿Cuántas Iteraciones en RANSAC?

Número de iteraciones:

$$
N =
\frac{\log(1-p)}
{\log(1-(1-e)^s)}
$$

donde:

- (s = 4) (para homografía)
- (e) = proporción de outliers
- (p) = probabilidad deseada (ej. 0.99)

Ejemplo:
Si 50% son outliers,
(s=4),
(p=0.99)

$$
N \approx 72
$$

Es computacionalmente eficiente .

## 22. Pipeline Geométrico Completo

1. Detectar características (SIFT, ORB, Harris).
2. Extraer descriptores.
3. Matching.
4. Aplicar RANSAC.
5. Estimar homografía con DLT + SVD.
6. Refinar con inliers.
7. Aplicaciones:

   - Image stitching (panoramas)
   - Rectificación
   - Realidad aumentada
   - SLAM

## 23. Cierre Conceptual

A nivel geométrico:

> Las homografías encapsulan la relación entre dos planos proyectivos.

A nivel algebraico:

> Resolver (A h = 0) con restricción usando SVD.

A nivel estadístico:

> RANSAC prioriza consenso sobre promedio.

A nivel práctico:

> La robustez es más importante que la precisión pura .

## Enlaces

### VIDEOS

- [How does pinhole camera work?](https://www.youtube.com/watch?v=wkRgKLchfoc)
- [Pinhole and Perspective Projection | Image Formation](https://www.youtube.com/watch?v=_EhY31MSbNM)
- [Camera Intrinsics and Extrinsics - 5 Minutes with Cyrill](https://www.youtube.com/watch?v=ND2fa08vxkY)
- [Intrinsic and Extrinsic Matrices | Camera Calibration](https://www.youtube.com/watch?v=2XM2Rb2pfyQ)
- [OpenCV Python Camera Calibration (Intrinsic, Extrinsic, Distortion)](https://www.youtube.com/watch?v=H5qbRTikxI4)
- [Quick Understanding of Homogeneous Coordinates for Computer Graphics](https://www.youtube.com/watch?v=o-xwmTODTUI)
- [Homogeneous Coordinates - 5 Minutes with Cyrill](https://www.youtube.com/watch?v=PvEl63t-opM)
- [3x3 Image Transformations | Image Stitching](https://www.youtube.com/watch?v=B8kMB6Hv2eI)
- [Computing Homography | Image Stitching](https://www.youtube.com/watch?v=l_qjO4cM74o)
- [Direct Linear Transform for Camera Calibration and Localization (Cyrill Stachniss)](https://www.youtube.com/watch?v=3NcQbZu6xt8)
- [Linear Systems of Equations, Least Squares Regression, Pseudoinverse](https://www.youtube.com/watch?v=PjeOmOz9jSY)
- [No One Taught SVD (Singular Value Decomposition) Like This](https://www.youtube.com/watch?v=llisH02KLrE)
- [Least Squares Regression and the SVD](https://www.youtube.com/watch?v=02QCtHM1qb4)
- [8 Point Algorithm - 5 Minutes with Cyrill](https://www.youtube.com/watch?v=z92eUJjIJeY)
- [RANSAC - 5 Minutes with Cyrill](https://www.youtube.com/watch?v=9D5rrtCC_E0)
- [Dealing with Outliers: RANSAC | Image Stitching](https://www.youtube.com/watch?v=EkYXjmiolBg)
- [RANSAC - Consenso de muestras aleatorias (Cyrill Stachniss)](https://www.youtube.com/watch?v=Cu1f6vpEilg)
- [RANSAC (Random Sample Consensus) Algorithm : Demonstrated in 2D](https://www.youtube.com/watch?v=BHNNz6jCuHw)
- [RANSAC - Regresión resistente a valores atípicos: algoritmo explicado claramente](https://www.youtube.com/watch?v=L9gTuNLglxs)
- [Ransac Algorithm - A brief Walkthrough](https://www.youtube.com/watch?v=QwIxskoWD9o)

### Páginas

- [Dissecting the Camera Matrix, Part 3: The Intrinsic Matrix](https://ksimek.github.io/2013/08/13/intrinsic/)
- [Camera Models](http://vision.stanford.edu/teaching/cs131_fall1314/lectures/lecture8_camera_models_cs131.pdf)
- [The Ultimate Guide to the RANSAC Algorithm](https://www.thinkautonomous.ai/blog/ransac-algorithm/)
- [Machine Learning Concept 69 : Random Sample Consensus (RANSAC).](https://medium.com/@ChandraPrakash-Bathula/machine-learning-concept-69-random-sample-consensus-ransac-e1ae76e4102a)
- [How does the RANSAC algorithm relate to computer vision?](https://milvus.io/ai-quick-reference/how-does-the-ransac-algorithm-relate-to-computer-vision)
- [Overview of the RANSAC Algorithm](http://www.cse.yorku.ca/~kosta/CompVis_Notes/ransac.pdf)
- [Random Sample Consensus Explained](https://www.baeldung.com/cs/ransac)
- [In defence of the 8-point algorithm](https://users.cecs.anu.edu.au/~hartley/Papers/fundamental/electronic-submission/fundamental.pdf)
- [Marginal Notes for Hartley & Zisserman’s ‘Multiple View Geometry’](https://staff.fnwi.uva.nl/l.dorst/hz/hz.pdf)
- [DLT to/from intrinsic + extrinsic](https://biomech.web.unc.edu/dlt-to-from-intrinsic-extrinsic/)
- [Homography Estimation](https://medium.com/data-science/estimating-a-homography-matrix-522c70ec4b2c)
- [Singular Value Decomposition (SVD)](https://www.cse.unr.edu/~bebis/MathMethods/SVD/lecture.pdf)
- [Singular Value Decomposition (SVD): Part 2](https://dev.to/shlok2740/singular-value-decomposition-svd-part-2-183)
- [The Direct Linear Transform](https://www.baeldung.com/cs/direct-linear-transform)
- [Estimating the Homography Matrix with the Direct Linear Transform (DLT)](https://medium.com/@insight-in-plain-sight/estimating-the-homography-matrix-with-the-direct-linear-transform-dlt-ec6bbb82ee2b)
- [Deconstructing the Homography Matrix](https://medium.com/@insight-in-plain-sight/deconstructing-the-homography-matrix-35989ecc0b2)
- [Homography](https://medium.com/@shantanuparab99/homography-a690527f2e1b)
- [The Concept Of Homogeneous Coordinates](https://prateekvjoshi.com/2014/06/13/the-concept-of-homogeneous-coordinates/)
- [Projective Geometry for Image Analysis](https://inria.hal.science/inria-00548361v1/document)
