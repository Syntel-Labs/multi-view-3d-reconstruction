# Semana 4 – Características Locales

Visión por Computadora e Inteligencia Artificial

## 1. Rol de las características locales en el pipeline de visión

En este módulo se aborda uno de los problemas centrales de la visión por computadora moderna: **la correspondencia entre imágenes**.
El objetivo es identificar puntos clave que representen la **misma estructura física** en imágenes distintas, aun cuando estas difieran en:

- Iluminación
- Rotación
- Escala
- Perspectiva
- Ruido u oclusiones parciales

La solución no consiste en comparar píxeles directamente, sino en **detectar estructuras estables** y describirlas mediante **huellas numéricas** robustas.

Este enfoque conecta directamente con:

- Semana 1: imagen como función y tensor numérico
- Semana 2: gradientes, convolución y operadores diferenciales
- Semana 3: suavizado gaussiano, frecuencia y estructura

## 2. De detección a descripción

Inicialmente, los algoritmos solo detectaban esquinas.
Sin embargo, detectar un punto no es suficiente: **necesitamos reconocerlo nuevamente** en otra imagen.

Esto da lugar a dos etapas claramente diferenciadas:

1. **Detección**: encontrar dónde están los puntos interesantes
2. **Descripción**: representar cada punto mediante un vector numérico invariante

La descripción permite comparar puntos de imágenes distintas incluso bajo transformaciones geométricas.

## 3. Harris: respuesta, umbral y supresión de no-máximos

### 3.1 Matriz de segundo momento y eigenvalores

Recordando la matriz de estructura:

$$
M =
\sum_{x,y} w(x,y)
\begin{bmatrix}
I_x^2 & I_x I_y \
I_x I_y & I_y^2
\end{bmatrix}
$$

Los eigenvalores $\lambda_1$ y $\lambda_2$ describen la variación de intensidad en direcciones ortogonales.

- Ambos pequeños → región plana
- Uno grande y otro pequeño → borde
- Ambos grandes → esquina

Calcular eigenvalores explícitamente es costoso computacionalmente.

### 3.2 Función de respuesta de Harris

Harris propone evitar el cálculo directo de eigenvalores usando:

$$
R = \det(M) - k,(\text{trace}(M))^2
$$

donde:

$$
\det(M) = \lambda_1 \lambda_2
$$

$$
\text{trace}(M) = \lambda_1 + \lambda_2
$$

El parámetro $k$ es un **hiperparámetro empírico**, típicamente en el rango:

$$
k \in [0.04, 0.06]
$$

Esta expresión penaliza bordes y realza esquinas.

### 3.3 Umbralización

Una vez calculada la respuesta $R$ para cada píxel:

$$
\text{esquina si } R > \text{threshold}
$$

El umbral elimina regiones planas y bordes débiles.

### 3.4 Non-Maximum Suppression (NMS)

Incluso tras aplicar el umbral, aparecen múltiples respuestas cercanas.

La **supresión de no-máximos** conserva solo el máximo local en una vecindad, garantizando:

- Un solo punto por esquina real
- Mejor localización espacial
- Menor redundancia

Esto conecta con el concepto de máximos locales visto previamente en detección de bordes.

## 4. Invariancia a rotación y limitaciones de Harris

Las esquinas detectadas por Harris son **invariantes a la rotación**, ya que la matriz $M$ depende de magnitudes de gradiente y no de la orientación absoluta.

Sin embargo, Harris **no es invariante a escala**.
Un cambio de zoom altera la vecindad analizada y puede hacer desaparecer o aparecer esquinas.

Este problema motiva el desarrollo de **SIFT**.

## 5. SIFT: Scale-Invariant Feature Transform

SIFT resuelve explícitamente el problema de la escala.

La idea central es simple:

Si un punto es realmente importante, debería ser detectable **en múltiples escalas**.

### 5.1 Pirámide Gaussiana

SIFT construye una **pirámide de escalas** aplicando filtros gaussianos con diferentes desviaciones estándar $\sigma$:

$$
L(x,y,\sigma) = G(x,y,\sigma) * I(x,y)
$$

Esto elimina progresivamente ruido y altas frecuencias.

### 5.2 Laplaciano de Gaussiana (LoG)

El Laplaciano de Gaussiana corresponde a la segunda derivada espacial:

$$
\nabla^2 (G * I)
$$

- La primera derivada es cero en el centro de una mancha
- La segunda derivada presenta un extremo

La forma del filtro es conocida como **sombrero mexicano**, debido a:

- Pico central positivo
- Valles negativos alrededor

Este filtro amplifica regiones tipo **blob** (manchas sobre fondo).

### 5.3 Diferencia de Gaussianas (DoG)

Calcular LoG directamente es costoso.
SIFT utiliza una aproximación eficiente:

$$
\text{DoG}(x,y,\sigma) = L(x,y,k\sigma) - L(x,y,\sigma)
$$

La DoG se comporta de forma similar al Laplaciano de Gaussiana, pero con mucho menor costo computacional.

### 5.4 Detección de extremos en escala y espacio

SIFT busca máximos y mínimos locales en un volumen 3D:

- Dirección X
- Dirección Y
- Escala $\sigma$

Si un punto sobrevive al desenfoque y sigue siendo extremo, se considera **keypoint estable**.

## 6. Orientación e invariancia a rotación

Para lograr invariancia a rotación, SIFT:

- Calcula gradientes locales alrededor del punto
- Construye un histograma de orientaciones
- Asigna una orientación dominante al keypoint

Esto permite **normalizar la rotación** antes de describir el punto.

## 7. Descriptor SIFT

Detectar el punto es solo la mitad del proceso.

Para describirlo:

- Se toma una ventana alrededor del keypoint
- Se divide en subregiones
- Se construyen histogramas de gradientes

El resultado es un vector de:

$$
128 \text{ dimensiones}
$$

Este vector es la **huella digital del punto**, estable frente a:

- Rotación
- Escala
- Cambios moderados de iluminación

El costo computacional es alto debido a:

- Convoluciones gaussianas
- Operaciones en punto flotante
- Histograma de gradientes

## 8. ORB: eficiencia en tiempo real

ORB surge como alternativa a SIFT para escenarios donde:

- El tiempo es crítico
- El hardware es limitado
- Se requiere procesamiento en tiempo real

ORB combina:

- **FAST** para detección
- **BRIEF** para descripción

## 9. FAST: Features from Accelerated Segment Test

FAST evalúa un círculo de 16 píxeles alrededor de un píxel central.

Pregunta clave:

¿Existen al menos $n$ píxeles consecutivos que sean significativamente más brillantes o más oscuros que el centro?

Si la respuesta es sí, el punto se considera esquina.

Ventajas:

- Comparaciones simples
- Extremadamente rápido
- Ideal para detección masiva

Desventaja:

- No es invariante a escala
- Sensible al ruido si no se filtra previamente

## 10. BRIEF: descriptor binario

BRIEF no usa histogramas ni gradientes.

Funciona realizando pruebas binarias:

$$
\text{bit}_i =
\begin{cases}
1 & \text{si } I(p_a) > I(p_b) \
0 & \text{en otro caso}
\end{cases}
$$

El resultado es una cadena binaria de:

$$
256 \text{ bits}
$$

Ventajas:

- Muy rápido
- Bajo consumo de memoria
- Ideal para dispositivos móviles

ORB añade orientación a BRIEF para hacerlo **invariante a rotación**.

## 11. Comparativa de detectores y descriptores

| Algoritmo | Velocidad  | Invarianza escala | Invarianza rotación |
| --------- | ---------- | ----------------- | ------------------- |
| Harris    | Rápido     | No                | Sí                  |
| SIFT      | Lento      | Excelente         | Excelente           |
| ORB       | Muy rápido | Buena             | Buena               |

## 12. Matching entre imágenes

Una vez detectadas y descritas las características, se realiza el emparejamiento.

### 12.1 Fuerza bruta

Para descriptores SIFT:

$$
d = | \mathbf{f}_1 - \mathbf{f}_2 |_2
$$

Comparación exhaustiva, precisa pero lenta.

### 12.2 FLANN y vecinos aproximados

FLANN acelera la búsqueda usando estructuras de datos para vecinos más cercanos.

Para descriptores binarios (ORB) se usa la **distancia de Hamming**.

### 12.3 Distancia de Hamming

Se calcula con XOR:

$$
d_H = \sum (\mathbf{b}_1 \oplus \mathbf{b}_2)
$$

Cuenta cuántos bits difieren.

## 13. Filtrado: Lowe’s Ratio Test

Muchos matches son falsos positivos.

Se aplica el criterio:

$$
\frac{d_1}{d_2} < 0.75
$$

Si los dos vecinos más cercanos son muy similares, el match se rechaza.

Esto elimina coincidencias ambiguas y ruido.

## 14. Pipeline completo resumido

1. Detectar

   - Harris (eigenvalores) o FAST

2. Describir

   - SIFT (128D) u ORB (binario)

3. Emparejar

   - Distancia euclidiana o Hamming

4. Filtrar

   - Lowe’s Ratio Test

## 15. Más allá de los puntos: RANSAC

Las características permiten encontrar **puntos clave**, pero no garantizan coherencia geométrica.

Para eliminar outliers y encontrar transformaciones geométricas consistentes se usa **RANSAC**.

RANSAC:

- Ajusta modelos geométricos
- Ignora correspondencias erróneas
- Permite detectar objetos o escenas completas

Este será el puente hacia la siguiente semana.

## 16. Cierre conceptual

Desde el punto de vista humano:

Buscamos puntos que llamen la atención.

Desde el punto de vista matemático:

Buscamos máximos locales de variación bajo derivadas y suavizado.

Desde el punto de vista computacional:

Buscamos estabilidad, invariancia y eficiencia.

Con Harris, SIFT y ORB ya no solo vemos imágenes:
**podemos compararlas, alinearlas y entender su estructura**.

## Enlaces

[Introduction to Harris Corner Detector](https://medium.com/@deepanshut041/introduction-to-harris-corner-detector-32a88850b3f6)

[Harris Corners](https://www.cs.cmu.edu/~16385/s17/Slides/6.2_Harris_Corner_Detector.pdf)

[Introducción a SIFT (Transformación de características invariantes de escala)](https://medium.com/@deepanshut041/introduction-to-sift-scale-invariant-feature-transform-65d7f3a72d40)

[¿Qué es la Transformación de Características Invariante a la Escala (SIFT)?](https://blog.roboflow.com/sift/)

[Detección y seguimiento de objetos con el algoritmo ORB usando OpenCV](https://medium.com/thedeephub/detecting-and-tracking-objects-with-orb-using-opencv-d228f4c9054e)

[ORB (Oriented FAST and Rotated BRIEF)](https://docs.opencv.org/4.x/d1/d89/tutorial_py_orb.html)

[What is Feature Matching?](https://blog.roboflow.com/what-is-feature-matching/)

[Local Feature Matching](https://sites.cc.gatech.edu/classes/AY2016/cs4476_fall/results/proj2/html/sshah426/index.html)

[(NMS) Non Maximum Suppression explained in detail using example. NMS algorithm explained.](https://www.youtube.com/watch?v=v6lt0cGSHBI)

[6 code Foundations of Computer Vision Feature Detection and Matching](https://www.youtube.com/watch?v=fQZVG41T45g)

[OpenCV Python Harris Corner Detection](https://www.youtube.com/watch?v=1LzJlVUSL5k)

[Corner Detection | Edge Detection](https://www.youtube.com/watch?v=Z_HwkG90Yvw)

[OpenCV Python SIFT Feature Detection (SIFT Algorithm Explained + Code)](https://www.youtube.com/watch?v=flFbNka62v8)

[SIFT - 5 Minutes with Cyrill](https://www.youtube.com/watch?v=4AvTMVD9ig0)

[SIFT | Scale Invariant Feature Transform | Computer Vision (Python)](https://www.youtube.com/watch?v=wpyGaQtRVz4)

[SIFT Detector | SIFT Detector](https://www.youtube.com/watch?v=ram-jbLJjFg)

[OpenCV Python ORB Feature Detection (ORB Algorithm Explained)](https://www.youtube.com/watch?v=0sPlnrEMyYk)

[ORB (Oriented FAST and Rotated BRIEF) || Feature Descriptor: ORB || Computer Vision Full Course](https://www.youtube.com/watch?v=9IFc4HshCU8)

[ORB Explained From Pixels to Features with Numerical Examples](https://www.youtube.com/watch?v=gV6gKVHVoOU)

[OpenCV Python SURF Feature Detection (SURF Algorithm Explained + Code)](https://www.youtube.com/watch?v=PBTrwymDVCg)
