# Visión por Computadora – Semana 2: Filtrado y Convolución

## Introducción al módulo

Esta semana daremos el paso fundamental de la **representación al procesamiento**.
Hasta ahora, hemos tratado las imágenes como matrices estáticas de números, pero para que una computadora pueda “ver”, necesitamos analizar **cómo se relacionan los píxeles entre sí**.

En este módulo aprenderemos la **matemática detrás de la Convolución**, la operación motor que impulsa desde el procesamiento clásico hasta las redes neuronales modernas. Veremos cómo manipular una imagen para **reducir ruido**, **resaltar información relevante** y **preparar los datos visuales** para análisis posteriores.

Nos centraremos en el diseño y aplicación de **filtros lineales**, el uso del **Filtro Gaussiano** para limpieza de escenas, el cálculo de **gradientes** con operadores como **Sobel**, y culminaremos con el estudio del **Algoritmo de Canny**, estándar de facto en detección de bordes.

## Motivación general

En clases anteriores se analizó el procesamiento **a nivel de un solo píxel**. En esta etapa se extiende el análisis a **vecindades de píxeles**, lo que da lugar a la **convolución**.  
Este enfoque es fundamental porque:

- Las imágenes reales contienen **ruido inherente a la captura**.
- Analizar un solo píxel maximiza el error en presencia de ruido.
- Las **operaciones de vecindad** permiten extraer **características relevantes** y reducir información irrelevante.
- El filtrado actúa como **preprocesamiento** para algoritmos más complejos como **Canny**, mejorando la predicción y estabilidad del sistema.

Se estudian dos dominios:

- **Espacial (píxeles)**: filtrado directo sobre la imagen.
- **Frecuencia (Fourier)**: se verá posteriormente.

## Convolución

### Intuición general

La convolución es una operación matemática que combina:

- Una **señal de entrada** (imagen, audio, etc.).
- Una **respuesta al impulso** (kernel o filtro).

En imágenes, permite resumir la información local de una región para producir un nuevo valor de píxel más robusto.

### Proceso matemático (1D)

1. **Reflejar el kernel** (flip).
2. **Desplazarlo** sobre la señal.
3. **Multiplicar y sumar** (integrar).

Formalmente:
$$
(f * g)(x) = \int f(\tau)\, g(x - \tau)\, d\tau
$$

### Diferencia con correlación cruzada

- La **convolución** invierte el kernel.
- La **correlación** no lo hace.
- Si el kernel es **simétrico** (ej. Gaussiano), ambas producen el mismo resultado.
- Si es **asimétrico**, el resultado cambia.

### Convolución en 2D

En imágenes, la operación se extiende a dos dimensiones y se expresa como una **doble sumatoria**.  
El kernel (matriz pequeña) se desplaza sobre la imagen (matriz grande), calculando un **producto punto** para cada píxel.

Esto:

- Reduce dimensionalidad local.
- Pierde información puntual irrelevante.
- Conserva estructura útil.

## Padding (relleno)

Al aplicar convolución en los bordes, el kernel se sale de la imagen. Para manejar esto se usa **padding**, principalmente para:

- Mantener el tamaño de la imagen.
- Evitar perder información en los bordes.
- Facilitar concatenación de etapas posteriores.

### Estrategias comunes

- **Zero padding**: relleno con ceros (introduce bordes negros).
- **Replicate / Clamp**: repite el último píxel válido.
- **Reflect / Mirror**: refleja la imagen (mejor continuidad visual).

El padding por reflexión **minimiza discontinuidades** y falsos bordes.

## Filtros lineales y suavizado

### Box Filter (promedio)

- Promedia los valores dentro del kernel.
- Reduce ruido de forma simple.

**Problemas**:

- Desenfoque agresivo.
- Bordes cuadrados.
- Introduce artefactos (ringing).
- Pierde información estructural y puede crear detalles inexistentes.

### Filtro Gaussiano

Alternativa preferida al promedio.

Características:

- Mayor peso en el centro del kernel.
- Peso decreciente hacia los vecinos.
- Controlado por $\sigma$, que define la dispersión.

Propiedades clave:

- Suaviza sin introducir artefactos fuertes.
- Reduce ruido preservando bordes relevantes.
- Es **separable**, reduciendo complejidad de:

$$
O(n^2 k^2) \rightarrow O(n^2 \cdot 2k)
$$

## Gradientes y detección de bordes (Sobel)

### Concepto de borde

Un borde es un **cambio brusco de intensidad**.  
Matemáticamente, esto se modela con **derivadas**.

En imágenes discretas se usan **diferencias finitas**.

### Operador Sobel

- Aproxima derivadas espaciales mediante convolución.
- Calcula:
  - $G_x$: cambios horizontales (bordes verticales).
  - $G_y$: cambios verticales (bordes horizontales).

Magnitud del gradiente:
$$
G = \sqrt{G_x^2 + G_y^2}
$$

Dirección del gradiente:
$$
\theta = \arctan2(G_y, G_x)
$$

Sobel:

- Suaviza y deriva simultáneamente.
- Responde con 0 en regiones planas.
- Resalta cambios reales de brillo.

## Algoritmo de Canny

Sobel es solo una **operación**.  
Canny es un **pipeline completo** (1986), aún vigente, enfocado en optimización.

### Objetivos

- Bordes precisos.
- Líneas finas.
- Alta relación señal–ruido.

### Etapas

1. **Suavizado Gaussiano**
   - Reduce ruido.
   - La derivada es altamente sensible al ruido.
   - $\sigma$ controla el nivel de detalle.

2. **Gradiente (Sobel)**
   - Cálculo de $G_x, G_y$.
   - Magnitud y orientación.
   - La orientación se discretiza (4 direcciones).

3. **Non-Maximum Suppression (NMS)**
   - Sobel detecta “montañas”.
   - Canny conserva solo la “cima”.
   - Adelgaza los bordes eliminando respuestas no máximas.

4. **Hysteresis Thresholding**
   - Umbral doble:
     - $G > T_{high}$: borde fuerte.
     - $G < T_{low}$: descartado.
     - Entre ambos: borde débil.
   - Un borde débil se conserva **solo si está conectado** a uno fuerte.

Esto evita:

- Bordes punteados.
- Pérdida de continuidad.
- Sensibilidad a vibraciones e iluminación variable.

## Resumen conceptual

- **Convolución**: operación base.
- **Gaussiano**: reducción de ruido.
- **Sobel**: cálculo de gradientes.
- **Canny**: sistema optimizado para extraer geometría.

Canny transforma datos masivos en **información estructural**, facilitando la interpretación por sistemas de visión artificial.

### Convolución – intuición y fundamentos matemáticos

- **[But what is a convolution?](https://youtu.be/KuXjwB4LzSA)**

  Explicación visual e intuitiva del concepto de convolución desde un enfoque matemático general.

- **[What is convolution? This is the easiest way to understand](https://youtu.be/QmcoPYUfbJ8)**
  
  Introducción simplificada enfocada en la intuición paso a paso.

- **[Convolution in 5 Easy Steps](https://youtu.be/aMaw4EumwyE)**

  Desglose procedural de la operación de convolución aplicado a señales e imágenes.

- **[The Convolution of Two Functions | Definition & Properties](https://youtu.be/AgKQQtEc9dk)**
  
  Enfoque matemático formal sobre convolución y sus propiedades fundamentales.

- **[Intuitive Guide to Convolution](https://betterexplained.com/articles/intuitive-convolution/)**
  
  Artículo que conecta la intuición conceptual con aplicaciones prácticas.

- **[Understanding “convolution” operations in CNN](https://medium.com/analytics-vidhya/convolution-operations-in-cnn-deep-learning-compter-vision-128906ece7d3)**
  
  Relación directa entre convolución clásica y su uso en redes neuronales convolucionales.

### Filtros lineales y suavizado

- **[Linear Image Filters | Image Processing I](https://youtu.be/-LD9MxBUFQo)**
  
  Introducción a filtros lineales y su efecto sobre imágenes digitales.

- **[How Blurs & Filters Work – Computerphile](https://youtu.be/C_zFhWdM4ic)**
  
  Explicación conceptual del efecto de los filtros de suavizado.

- **[OpenCV Python Gaussian Filtering](https://youtu.be/Ud5f1P1lr8Q)**
  
  Implementación práctica del filtro Gaussiano usando OpenCV.

- **[Understanding the Gaussian Filter](https://himani-gulati.medium.com/understanding-the-gaussian-filter-c2cb4fb4f16b)**
  
  Artículo centrado en la intuición y comportamiento del filtro Gaussiano.

- **[What is Gaussian blur in image processing?](https://www.educative.io/answers/what-is-gaussian-blur-in-image-processing)**
  
  Explicación conceptual del desenfoque Gaussiano y sus aplicaciones.

- **[This is the Difference of Gaussians](https://youtu.be/5EuYKEvugLU)**
  
  Comparación entre filtros Gaussianos y su uso para detección de estructuras.

### Gradientes y operador Sobel

- **[Finding the Edges (Sobel Operator) – Computerphile](https://youtu.be/uihBwtPIBxM)**
  
  Introducción conceptual a la detección de bordes mediante gradientes.

- **[Sobel Edge Detection – Computer Vision (Python)](https://youtu.be/87Wtr4rK0Ns)**
  
  Implementación práctica del operador Sobel en Python.

- **[Image Processing Tutorial – Sobel Edge Detection Solved Example](https://youtu.be/Yz7h9L4gecQ)**
  
  Ejemplo resuelto paso a paso del cálculo de bordes con Sobel.

- **[Edge Detection Using Gradients](https://youtu.be/lOEBsQodtEQ)**
  
  Explicación general del enfoque por gradientes para detección de bordes.

- **[Understanding Use Of Image Gradients: Gaussian Blur, Sobel & Laplacian](https://medium.com/@chinmayiadsul/understanding-use-of-image-gradients-gaussian-blur-sobel-laplacian-explained-simply-e108b744eaf3)**
  
  Relación entre suavizado, gradientes y detección de bordes.

- **[Sobel Edge Detection vs. Canny Edge Detection](https://www.geeksforgeeks.org/computer-vision/sobel-edge-detection-vs-canny-edge-detection-in-computer-vision/)**
  
  Comparación conceptual entre Sobel y Canny.

### Algoritmo de Canny

- **[Canny Edge Detector – Computerphile](https://youtu.be/sRFM5IEqR2w)**
  
  Explicación conceptual del algoritmo completo y su motivación.

- **[Canny Edge Detector | Edge Detection](https://youtu.be/hUC1uoigH6s)**
  
  Descripción general de las etapas del algoritmo.

- **[Lecture 4.4: Edge Detection – Canny Edge Detection](https://youtu.be/bFq9_F7q1Eo)**
  
  Enfoque académico sobre los pasos matemáticos del algoritmo.

- **[OpenCV Python Canny Edge Detection](https://youtu.be/PS7zHKwXWRM)**
  
  Implementación práctica del detector de Canny en OpenCV.

- **[The Canny Edge Detector: Mathematical Foundations and Implementation](https://medium.com/@zar_373/the-canny-edge-detector-mathematical-foundations-and-implementation-of-a-computer-vision-c47e83d6e792)**
  
  Artículo profundo sobre los fundamentos matemáticos y detalles de implementación.

- **[What is Canny edge detection?](https://www.educative.io/answers/what-is-canny-edge-detection)**
  
  Explicación general del algoritmo y su propósito en visión por computadora.
