# Visión por Computadora – Semana 6 – Workshop Panoramas y Stitching

## 1. Fundamentos Geométricos: Modelo Pinhole

La formación de imagen se modela mediante proyección central. Un punto 3D $X = (X,Y,Z,1)^T$ se proyecta en el plano imagen como:

$$
\lambda
\begin{bmatrix}
u \ v \ 1
\end{bmatrix}
=============

K [R \mid t]
\begin{bmatrix}
X \ Y \ Z \ 1
\end{bmatrix}
$$

donde:

- $K$ = matriz intrínseca
- $R,t$ = parámetros extrínsecos
- $\lambda$ = factor de escala (coordenadas homogéneas)

Esto es clave porque en panoramas **queremos que solo cambie $R$**, no $t$.

## 2. Problema del Campo de Visión (FOV)

Las cámaras tienen FOV limitado. Para capturar una escena amplia:

- Se toman imágenes superpuestas.
- Se asume iluminación relativamente consistente.
- Se requiere superposición mínima (~30%) para estabilidad en el matching.

Matemáticamente, si el solape es bajo, disminuye la probabilidad de encontrar suficientes correspondencias robustas para estimar una homografía estable.

## 3. Condición Clave del Panorama

Para que dos imágenes estén relacionadas por una **homografía global**, debe cumplirse una de estas condiciones:

### Caso 1: Escena Plana

Todos los puntos satisfacen una ecuación de plano:

$$
\pi: n^T X + d = 0
$$

### Caso 2: Rotación Pura

Si la cámara rota sobre su centro óptico:

$$
C_1 = C_2
$$

No existe traslación, solo:

$$
P_2 = K R K^{-1}
$$

En este caso la relación entre imágenes es una homografía inducida por rotación.

## 4. El Enemigo: Paralaje

El paralaje ocurre cuando:

$$
C_1 \neq C_2
$$

La disparidad está relacionada con la profundidad:

$$
\text{disparidad} \propto \frac{1}{Z}
$$

Si $Z \to \infty$, la traslación es despreciable → homografía funciona.
Si hay objetos cercanos → aparecen "fantasmas".

Por eso, panoramas clásicos asumen rotación pura.

## 5. Homografía

Una homografía es una transformación proyectiva:

$$
\begin{bmatrix}
x' \ y' \ 1
\end{bmatrix}
\sim
H
\begin{bmatrix}
x \ y \ 1
\end{bmatrix}
$$

con

$$
H =
\begin{bmatrix}
h_{11} & h_{12} & h_{13} \
h_{21} & h_{22} & h_{23} \
h_{31} & h_{32} & h_{33}
\end{bmatrix}
$$

Propiedades:

- 8 grados de libertad (escala arbitraria).
- Preserva colinealidad.
- No preserva paralelismo ni ángulos.

## 6. Estimación con DLT

Queremos resolver:

$$
A h = 0
$$

donde $h$ es el vector de 9 elementos de $H$.

Cada correspondencia $(x,y) \leftrightarrow (x',y')$ produce 2 ecuaciones lineales.

Se necesitan mínimo 4 pares:

$$
4 \times 2 = 8 \text{ ecuaciones}
$$

Se impone restricción:

$$
||h|| = 1
$$

La solución es el vector singular asociado al menor valor singular de $A$ (SVD).

Problema: mínimos cuadrados falla ante outliers.

## 7. RANSAC

Algoritmo robusto:

1. Tomar 4 correspondencias aleatorias.
2. Calcular $H$ exacta.
3. Medir error de reproyección:

$$
e_i = ||x'_i - H x_i||
$$

4. Contar inliers si:

$$
e_i < \tau
$$

5. Repetir $N$ veces.
6. Recalcular con todos los inliers.

Número de iteraciones:

$$
N = \frac{\log(1-p)}{\log(1-w^s)}
$$

donde:

- $p$ = probabilidad deseada
- $w$ = proporción estimada de inliers
- $s=4$

## 8. Pipeline Completo de Stitching

### 1. Detección y descripción

Convertir a escala de grises.
Detectar con SIFT u ORB.

### 2. Matching

Usar FLANN o BruteForce.

Filtro de Lowe:

$$
\frac{d_1}{d_2} < 0.7
$$

Reduce drásticamente falsos positivos.

### 3. Estimación

Usar:

$$
H = \text{findHomography}(pts_1, pts_2, \text{RANSAC})
$$

### 4. Warping

Transformación:

$$
x' = Hx
$$

Se usa **mapeo inverso** para evitar huecos:

$$
x = H^{-1} x'
$$

Interpolación:

- Bilineal
- Bicúbica

### 5. Canvas

Si imagen A es fija:

$$
W_{total} = W_A + W_B
$$

$$
H_{total} = \max(H_A, H_B)
$$

## 9. Problema del Warp: Huecos Negros

Al aplicar homografía, el rectángulo se convierte en cuadrilátero irregular.

Solución correcta: Máscaras.

1. Crear máscara binaria:

$$
M(x,y) =
\begin{cases}
1 & \text{si hay información}\
0 & \text{si es fondo negro}
\end{cases}
$$

2. Invertir máscara.
3. Combinar usando operaciones booleanas.

## 10. Blending

### Promedio Ingenuo

$$
I = \frac{I_1 + I_2}{2}
$$

Genera fantasmas.

### Linear Blending

$$
I = \alpha(x) I_1 + (1-\alpha(x)) I_2
$$

donde $\alpha(x)$ es rampa lineal en zona de solape.

### Multiband Blending

Descomposición en pirámide Gaussiana:

$$
I = \sum_{k} L_k
$$

Mezcla bajas frecuencias suavemente y altas frecuencias abruptamente.

Es estándar industrial.

## 11. Orientación Train vs Query

Si la imagen izquierda es referencia:

- Se fija en coordenada $(0,0)$.
- Se transforma la derecha.

Invertir genera coordenadas negativas y complejiza la lógica.

## 12. Aplicaciones de Homografía

- Panoramas
- Rectificación de documentos
- Corrección de perspectiva
- CamScanner-like apps
- AR planar tracking

## 13. Transición a Estéreo

Panorama:

- $C_1 = C_2$
- Relación: Homografía
- Resultado: Imagen 2D extendida

Estéreo:

- $C_1 \neq C_2$
- Relación: Geometría epipolar
- Matriz fundamental $F$:

$$
x'^T F x = 0
$$

Aquí el paralaje es útil → permite estimar profundidad.

## 14. Errores Comunes que Faltaban en tus Notas

- No normalizar puntos antes de DLT (mejora estabilidad numérica).
- No usar umbral adecuado en RANSAC.
- No usar mapeo inverso en warp.
- No considerar interpolación.
- No recortar bordes negros al final.

## Enlaces

### Videos

- [Compute the homography using Direct linear transformation (DLT) in Matlab](https://www.youtube.com/watch?v=Hi9EFtzPl8Y)
- [Direct Linear Transform - 5 Minutes with Cyrill](https://www.youtube.com/watch?v=Fdwa0UEJ_F8)
- [Camera Calibration Based on Direct Linear Transform Explained](https://www.youtube.com/watch?v=oFZQykvEw14)
- [RANSAC - 10 - Introduction to Computer Vision - CMPT 361](https://www.youtube.com/watch?v=-XX6SUGFCbU)
- [Dealing with Outliers: RANSAC | Image Stitching](https://www.youtube.com/watch?v=EkYXjmiolBg)
- [RANSAC (Random Sample Consensus) Algorithm : Demonstrated in 2D](https://www.youtube.com/watch?v=BHNNz6jCuHw)
- [How a 40-Year-Old Trick Solves Seamless Image Blending](https://www.youtube.com/watch?v=U7qa7i0K9C4)
- [OpenCV: Gaussian and Laplacian Pyramids, Blending Edges, Move Named Window](https://www.youtube.com/watch?v=_B9kP_N8YjQ)
- [Image filtering: pyramids: Laplacian pyramid](https://www.youtube.com/watch?v=QNxJoglVS1Q)
- [Stitching a Panorama - What is Perspective](https://www.youtube.com/watch?v=FlmSEaep7Bg)
- [Epipolar Geometry : Fundamental Matrix (Visualization in Blender)](https://www.youtube.com/watch?v=PFQ3A7TEMIo)
- [Epipolar Geometry: Solving the fundamental Matrix](https://www.youtube.com/watch?v=Xmcu_XPrTho)
- [Photogrammetry II - 03a - Epipolar Geometry and Essential Matrix (2015/16)](https://www.youtube.com/watch?v=vNG0uJR48XE)
- [Estimating Fundamental Matrix | Uncalibrated Stereo](https://www.youtube.com/watch?v=izpYAwJ0Hlw)
- [OpenCV Python Depth Map Stereo Vision for Depth Estimation (Algorithm and Code)](https://www.youtube.com/watch?v=gffZ3S9pBUE)
- [Image analysis: stereo: depth from stereo](https://www.youtube.com/watch?v=KSYVobIeY_4)
- [OpenCV: Stereo Vision Disparity (Depth Map)](https://www.youtube.com/watch?v=5LrAhSHNIJU)
- [First Principles of Computer Vision](https://www.youtube.com/watch?v=1EJ84QqkxWc)

### Documentos

- [Estimating the Homography Matrix with the Direct Linear Transform (DLT)](https://medium.com/@insight-in-plain-sight/estimating-the-homography-matrix-with-the-direct-linear-transform-dlt-ec6bbb82ee2b)
- [Direct Linear Transform](https://www.cs.cmu.edu/~16385/s17/Slides/10.2_2D_Alignment__DLT.pdf)
- [How does the RANSAC algorithm relate to computer vision?](https://milvus.io/ai-quick-reference/how-does-the-ransac-algorithm-relate-to-computer-vision)
- [The Ultimate Guide to the RANSAC Algorithm](https://www.thinkautonomous.ai/blog/ransac-algorithm/)
- [How does the Lowe's ratio test work?](https://stackoverflow.com/questions/51197091/how-does-the-lowes-ratio-test-work)
- [Introduction to SIFT( Scale Invariant Feature Transform)](https://medium.com/@deepanshut041/introduction-to-sift-scale-invariant-feature-transform-65d7f3a72d40)
- [3D Object Detection with Depth Estimation from Stereo Cameras: Challenges and HITNet Deep Learning Innovations](https://medium.com/@az.tayyebi/3d-object-detection-with-depth-estimation-from-stereo-cameras-challenges-and-hitnet-deep-learning-431392dfc137)
- [Depth from Stereo](https://www.cs.toronto.edu/~fidler/slides/2015/CSC420/lecture12.pdf)
