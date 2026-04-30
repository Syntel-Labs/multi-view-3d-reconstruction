# Visión por Computadora – Semana 1: Introducción e Imágenes Digitales

## Introducción al curso

Este es un **curso avanzado de Visión por Computadora** que integra los fundamentos matemáticos de la visión clásica con técnicas modernas de **Inteligencia Artificial**. El objetivo es que el estudiante sea capaz de resolver problemas visuales **end-to-end**, desde la adquisición de la imagen hasta la toma de decisiones automatizada en escenarios reales de la industria.

El curso está diseñado para estudiantes de **5to año**, por lo que asume madurez técnica y conocimientos previos en **álgebra lineal, probabilidad, estadística y programación**. No se trata solo de usar modelos, sino de **entender profundamente qué sucede con los datos visuales en cada etapa del pipeline**.

## Estructura general del curso

### Visión clásica y geometría

Se construye una base matemática sólida para entender la imagen como una señal:

- Procesamiento matemático de imágenes.
- Filtros y operaciones espaciales.
- Transformaciones proyectivas.
- Algoritmos geométricos robustos como **RANSAC**.
- Descriptores locales para alineación de imágenes, panoramas y reconstrucción 3D.

### Aprendizaje profundo aplicado a visión

Se estudia la evolución de las arquitecturas neuronales:

- Motivación y diseño de redes convolucionales.
- Arquitecturas clásicas como **AlexNet** y **VGG** para entender extracción de características y mapas de activación.
- Transición hacia arquitecturas modernas como **ResNet**.
- Uso de **Transfer Learning** en problemas reales.

### Visión computacional moderna y generativa

Aplicaciones avanzadas:

- Detección de objetos en tiempo real (familia **YOLO**).
- Segmentación semántica (**U-Net**).
- Seguimiento de objetos en video.
- Introducción a **Vision Transformers (ViT)**.
- Modelos generativos: **GANs** y **Modelos de Difusión**, usados en generación de imágenes y contenido sintético.

## Inteligencia Artificial y madurez profesional

Aunque el interés natural es entrenar modelos profundos, un ingeniero senior entiende que **un modelo sofisticado no compensa datos defectuosos**.
Esta semana rompe la idea de la imagen como “foto” y la redefine como un **tensor numérico multidimensional**.

Se analiza:

- La física de la adquisición de imágenes.
- Las limitaciones matemáticas de los sensores.
- Por qué la intuición humana del color (RGB) suele ser incorrecta para algoritmos.

## ¿Por qué esta semana es crítica?

En la industria, el principio **GIGO (Garbage In, Garbage Out)** explica la mayoría de fracasos en proyectos de visión.
Si no se entiende:

- Cómo la luz se convierte en una matriz de enteros `uint8`.
- Cómo afecta el ruido de cuantización.
- Por qué una operación lineal mal aplicada destruye información.

entonces los modelos de Deep Learning **no convergen** y el ingeniero no sabe por qué.

## Objetivos de la semana

Al finalizar este módulo serás capaz de:

- Comprender el **pipeline completo de visión**.
- Manipular imágenes como **tensores NumPy**, controlando tipos de datos y memoria.
- Usar **espacios de color perceptuales** (HSV, Lab).
- Aplicar **operaciones matemáticas por píxel** para preprocesamiento profesional.

## Imagen digital como tensor

Una imagen no es una fotografía, es una **matriz numérica**:

- Dimensiones: alto × ancho × canales.
- Cada píxel es un vector de valores.
- La computadora solo entiende **números**, no colores.

## Espacios de color

### RGB y BGR

- RGB es intuitivo para humanos, pero inestable para visión artificial.
- OpenCV usa **BGR** por razones históricas.
- Error común: visualizar BGR como RGB y obtener colores incorrectos.

### HSV

HSV desacopla el color del brillo:

- **H (Hue)**: matiz, indica el color (ángulo).
- **S (Saturation)**: pureza del color (radio).
- **V (Value)**: brillo (altura).

Geométricamente se representa como un **cono**.
OpenCV representa:

- H en rango `[0,179]` (no `[0,360]`) por limitaciones de 8 bits.
- Esto es consecuencia directa de representar colores como enteros.

Ventaja clave:

- En escenarios día/noche o con variaciones de iluminación, **HSV mantiene estabilidad**, mientras RGB cambia drásticamente.

### LAB

- Diseñado para aproximarse a la **percepción humana**.
- Ideal para **comparaciones de color con criterio humano**.
- Muy usado en análisis donde la percepción visual es crítica.

### YCbCr

- Usado en video digital y compresión JPEG.
- **Y**: luminancia (brillo).
- **Cb/Cr**: crominancia (color).

El ojo humano es más sensible al brillo que al color, por eso:

- Se comprime más el color que la luminancia.
- Mejora eficiencia de transmisión.
- En video en tiempo real puede ser hasta **60% más eficiente** para entrenamiento.

## Tipos de datos y errores silenciosos

Las imágenes suelen almacenarse como:

- `uint8`: valores `[0,255]`.

Problemas comunes:

- **Overflow**: operaciones que exceden 255 y “dan la vuelta” por módulo 256.
- **Clipping**: valores forzados a 0 o 255.
- **Casting**: conversiones implícitas entre `uint8` y `float32`.
- **Costo computacional**: operar en `float` es más caro, pero necesario.

Regla fundamental:

- Operar en **float32** dentro del pipeline.
- Al final, aplicar **clipping** y convertir a `uint8`.

Esto permite preservar información y evitar imágenes más oscuras o claras que el original.

## Operaciones puntuales

Una operación puntual depende de **un solo píxel**, no de sus vecinos.

- Son altamente paralelizables.
- Ideales para GPU o tablas de búsqueda (lookup tables).

Modelo general:
$g(x',y) = T[f(x',y)]$

Modelo lineal:
$g = \alpha f + \beta$

Parámetros:

- $\alpha$: controla el **contraste**.
- $\beta$: controla el **brillo**.

Ejemplo típico de filtros tipo Instagram.

### Contrast stretching

Se busca:

- Encontrar el píxel más oscuro y más claro.
- Estirar dinámicamente el rango a `[0,255]`.

Es similar a un **Min-Max Scaler**, pero:

- Asume linealidad.
- Puede destruir información.

### Ley de Weber–Fechner

Error fundamental:

- El ojo humano **no es lineal**.
- La percepción del brillo es logarítmica.

### Corrección gamma

Solución:
$v_{out} = A \cdot v_{in}^{\gamma}$

Donde:

- $v_{in} \in [0,1]$.
- $\gamma > 1$: oscurece y aumenta profundidad.
- $\gamma < 1$: aclara y expande sombras.

Esto simula la percepción humana.

## Histograma

Describe la distribución de intensidades:

- Eje X: niveles de intensidad `[0,255]`.
- Eje Y: cantidad de píxeles.

Diagnóstico rápido:

- **Subexpuesta**: histograma a la izquierda.
- **Sobreexpuesta**: histograma a la derecha.

Si el histograma es malo:

- Detección de bordes.
- Segmentación.
- Clasificación.
  también fallarán.

### CLAHE

Técnica avanzada:

- Mejora contraste **local**, no global.
- Fundamental en imágenes médicas como radiografías.

## Buenas prácticas con OpenCV

- Usar **NumPy vectorizado**, evitar `for` y `while`.
- Usar `cv2.add` y `cv2.subtract`, no `+` o `-`.
- Cuidar overflow.
- Recordar la trampa **BGR vs RGB**.

## Ideas clave de la semana

- Imagen = tensor numérico.
- GIGO domina todo el pipeline.
- No confiar en lo que “se ve”.
- Analizar histogramas.
- Usar HSV o Lab para análisis robusto.
- Operar en float, almacenar en uint8.

## Descripción de recursos y enlaces

### Representación de imágenes y píxeles

- **[Images, Pixels and RGB](https://youtu.be/15aqFQQVBWU)**

  Explica cómo una imagen digital se representa como píxeles y canales de color.

- **[Images as Functions Explained](https://youtu.be/B31Rs_naPE0)**

  Presenta la imagen como una función matemática definida sobre un dominio espacial.

### Pipeline de visión por computadora

- **[How Computer Vision Works](https://youtu.be/OcycT1Jwsns)**

  Visión general del pipeline completo de visión por computadora.

- **[Computer Vision Explained in 5 Minutes](https://youtu.be/puB-4LuRNys)**

  Resumen de alto nivel del campo y sus aplicaciones.

- **[Image Sensing Pipeline](https://youtu.be/bVSV3XZ1Jrs)**

  Describe el pipeline físico-matemático desde la captura hasta la imagen digital.

### Formación de la imagen y sensores

- **[Types of Image Sensors](https://youtu.be/nsPvcX-_4KU)**

  Tipos de sensores de imagen y sus limitaciones físicas.

- **[Image Formation](https://youtu.be/_QjxbQKY4ds)**

  Explica cómo la luz interactúa con el sensor para formar una imagen digital.

- **Image sensing and image formation model**

  Modelo matemático completo desde la luz hasta la imagen digital.
  [https://medium.com/@muhammad.a0625/image-sensing-and-image-formation-model-e875e6ede3bb](https://medium.com/@muhammad.a0625/image-sensing-and-image-formation-model-e875e6ede3bb)

### Color y percepción humana

- **[Computer Color is Broken](https://www.youtube.com/watch?v=LKnqECcg6Gw)**

  Analiza por qué el modelo RGB no refleja correctamente la percepción humana.

- **Understand and Visualize Color Spaces**

  Relación entre espacios de color y desempeño en modelos de ML y DL.
  [https://medium.com/data-science/understand-and-visualize-color-spaces-to-improve-your-machine-learning-and-deep-learning-models-4ece80108526](https://medium.com/data-science/understand-and-visualize-color-spaces-to-improve-your-machine-learning-and-deep-learning-models-4ece80108526)

- **Modelos de color HSL y HSB**

  Explicación conceptual y visual de modelos de color perceptuales.
  [https://aprenderuxui.com/modelos-de-color-hsl-y-hsb/aprender/uidesign/](https://aprenderuxui.com/modelos-de-color-hsl-y-hsb/aprender/uidesign/)

### Espacios de color y OpenCV

- **OpenCV Color Spaces (cv2.cvtColor)**

  Guía práctica sobre conversiones entre espacios de color en OpenCV.
  [https://pyimagesearch.com/2021/04/28/opencv-color-spaces-cv2-cvtcolor/](https://pyimagesearch.com/2021/04/28/opencv-color-spaces-cv2-cvtcolor/)
