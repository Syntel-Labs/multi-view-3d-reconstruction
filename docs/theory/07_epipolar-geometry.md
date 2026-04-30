# Semana 7 – Redes Neuronales en Imágenes y Visión Estéreo

Tras dominar panoramas y comprender cómo la geometría epipolar permite triangular profundidad en sistemas estéreo, damos el salto desde métodos geométricos tradicionales hacia **Redes Neuronales Convolucionales (CNNs)**. Este módulo conecta visión 3D, aprendizaje profundo y aplicaciones industriales modernas como robótica y conducción autónoma.

## 1. Contexto Actual en Arquitecturas de IA

- Los **Transformers** han impulsado el boom reciente en IA, pero requieren grandes recursos computacionales.
- Las **CNNs** siguen siendo el estándar de eficiencia en dispositivos móviles, cámaras inteligentes y sistemas embebidos.
- Levantar plataformas modernas implica costos significativos en hardware especializado.

### Generación de Imágenes

- Modelos como DALL·E, Midjourney, Grok y otros han revolucionado la generación visual.
- Los sistemas actuales no solo calculan: interpretan, generan y aprenden estrategias complejas.
- Las CNNs siguen siendo fundamentales en percepción, lógica visual y extracción de características.

## 2. Visión Estéreo y Profundidad

### 2.1 Visión Monocular

- Una sola cámara.
- Existe ambigüedad en profundidad.
- Difícil distinguir tamaño real vs. cercanía.

### 2.2 Visión Estéreo

- Dos cámaras separadas por un **baseline** $B$.
- Se basa en **triangulación**.
- Objetos cercanos presentan mayor desplazamiento.
- Objetos lejanos presentan menor desplazamiento.

La profundidad es inversamente proporcional a la disparidad.

## 3. De Panoramas a Geometría Epipolar

### 3.1 Panoramas y Homografía

- Se evita paralaje.
- Solo rotación: $C_1 = C_2$.
- Se usa homografía $H$ (matriz $3 \times 3$).
- Asume que todo es plano.
- Funciona cuando no hay traslación.

Problema: en el mundo real casi siempre hay paralaje.

### 3.2 Estéreo y Paralaje

- Si hay traslación: $C_1 \neq C_2$.
- Aparece disparidad.
- Permite estimar profundidad.

### Disparidad

$d = x_L - x_R$

## 4. Geometría Epipolar

- Reduce búsqueda 2D a 1D.
- Un punto en una imagen vive en una línea epipolar en la otra.
- Restricción epipolar:

$$
x'^T F x = 0
$$

Donde:

- $F$ = matriz fundamental.
- Representa un plano que pasa por ambos centros de cámara y el punto 3D.

### Fórmula de Profundidad

$$
Z = \frac{f \times B}{d}
$$

Donde:

- $f$ = distancia focal
- $B$ = baseline
- $d$ = disparidad

## 5. Limitaciones de Métodos Tradicionales

- Superficies sin textura (pared blanca).
- Oclusiones (objeto visible en una cámara pero no en otra).
- Matching de píxeles falla.
- Homografía no modela profundidad real.

Solución moderna: **CNNs para correspondencia robusta**.

## 6. Repaso de Redes Neuronales

### 6.1 Perceptrón

Relación lineal:

$$
y = wx + b
$$

Con activación no lineal:

- Sigmoid
- Tanh
- ReLU
- LeakyReLU

Permiten transformar relaciones lineales en no lineales.

### 6.2 Entrenamiento

- **Feedforward**: paso hacia adelante.
- **Backpropagation**: cálculo de gradientes.
- Optimización minimizando función de pérdida.

Millones de neuronas trabajando juntas generan abstracciones complejas.

## 7. Problema de Dimensionalidad en Imágenes

Una imagen es una matriz de intensidades $[0,255]$.

Imagen RGB = 3 matrices.

Ejemplo:

$256 \times 256 = 65,536$ valores.

Al aplanar:

- Se pierden relaciones espaciales.
- Demasiados parámetros.
- Maldición de la dimensionalidad.

## 8. Convolución: La Solución

Las CNNs:

- Extraen características locales automáticamente.
- Asumen que píxeles cercanos están relacionados.
- Usan kernels deslizantes.

## 9. Operación de Convolución

Definición:

$$
S(i,j) = (I * K)(i,j) = \sum_m \sum_n I(i-m, j-n) K(m,n)
$$

Donde:

- $I$ = imagen
- $K$ = kernel

Proceso:

1. Producto elemento a elemento.
2. Suma de productos.
3. Genera feature map.

### Ventajas

- Compartición de pesos.
- Invarianza local a traslación.
- Red aprende filtros automáticamente.

Detecta:

- Bordes
- Texturas
- Patrones

## 10. Arquitectura CNN Básica

Pipeline:

Imagen → Convolución → ReLU → Pooling → Convolución → Flatten → Fully Connected → Softmax

### Softmax

Convierte salida en distribución de probabilidades.

## 11. ReLU

$$
ReLU(x) = \max(0, x)
$$

- Elimina valores negativos.
- Acelera entrenamiento.
- Introduce no linealidad.

## 12. Padding

Problema: la imagen se reduce tras convolución.

Solución: agregar padding.

Zero padding:

- Añade ceros en bordes.
- Conserva información límite.

Para mantener tamaño:

$$
P = \frac{F - 1}{2}
$$

Donde:

- $F$ = tamaño del kernel.

## 13. Stride

Stride $S$ = pasos que avanza el kernel.

- $S = 1$ → pixel a pixel.
- $S = 2$ → reduce resolución.

Dimensión de salida:

$$
O = \left\lfloor \frac{W - F + 2P}{S} \right\rfloor + 1
$$

## 14. Pooling

Reduce dimensiones.

Tipos:

- Max Pooling
- Average Pooling

Ventajas:

- Reduce varianza.
- Evita sobreajuste.
- Introduce invariancia a pequeñas traslaciones.

## 15. Jerarquía de Características

CNNs aprenden de forma jerárquica:

1. Capas iniciales → bordes.
2. Capas intermedias → formas.
3. Capas profundas → objetos.

Se pasa de lo abstracto a lo semántico.

## 16. Aplicación a Visión Estéreo

Pipeline moderno:

Imagen izquierda + Imagen derecha → CNN → Feature maps → Matching profundo → Mapa de disparidad → Mapa de profundidad

Estrategias:

- Redes siamesas para comparación de parches.
- Regresión directa de disparidad.
- Supervisión por profundidad real.

Las CNN generan descriptores más robustos que métodos manuales.

## 17. Conclusiones Clave

- La convolución es el corazón de la visión computacional moderna.

- Padding y stride controlan dimensiones.
- Pooling resume información relevante.
- CNNs superan métodos clásicos en correspondencia estéreo.
- Profundidad depende de disparidad: $Z \propto \frac{1}{d}$.
- Arquitectura básica: Conv → Pool → FC → Softmax.
- Próximo paso: arquitecturas históricas como AlexNet.

## Enlaces

- [Lecture 6: Introduction to Convolutional Neural Networks](https://ubc-mds.github.io/DSCI_572_sup-learn-2/lectures/06_cnns-pt1.html)
- [A Basic Introduction to Convolutional Neural Network](https://dasher.wustl.edu/chem430/readings/basic-intro-cnn.pdf)
- [Lecture 14: Convolutional Neural Networks](https://www.cse.iitb.ac.in/~swaprava/courses/cs217/scribes/CS217_2024_lec14.pdf)
- [10-315 Notes Convolutional Neural Networks](https://www.cs.cmu.edu/~10315/notes/10315_S25_Notes_CNNs.pdf)
- [Stereo Vision and Depth Perception in Computer Vision](https://sumitkrsharma-ai.medium.com/stereo-vision-and-depth-perception-in-computer-vision-8aff8dd04e7c)
- [A complete walkthrough of convolution operations](https://viso.ai/deep-learning/convolution-operations/)
- [Convolutional Neural Networks](https://cs231n.stanford.edu/slides/2016/winter1516_lecture7.pdf)
- [Introduction to Epipolar Geometry and Stereo Vision](https://learnopencv.com/introduction-to-epipolar-geometry-and-stereo-vision/)

- [Epipolar Geometry | Uncalibrated Stereo](https://www.youtube.com/watch?v=6kpBqfgSPRc)
- [OpenCV Python Depth Map Stereo Vision for Depth Estimation (Algorithm and Code)](https://www.youtube.com/watch?v=gffZ3S9pBUE)
- [Simple Stereo | Camera Calibration](https://www.youtube.com/watch?v=hUVyDabn1Mg)
- [Clumsy Cyclops- How does Stereo Vision work?](https://www.youtube.com/watch?v=yfjMJfXMBcY)
- [Stereo 3D Vision (How to avoid being dinner for Wolves) - Computerphile](https://www.youtube.com/watch?v=O7B2vCsTpC0)
- [Stereo Vision Explained: How Depth Perception Works in Computer Vision](https://www.youtube.com/watch?v=wloN0_-QOe4)
- [Introducción a las redes neuronales convolucionales (ML Zero to Hero, parte 3)](https://www.youtube.com/watch?v=mO1fNuOhjtw)
- [AI- Aprende como hacer visión por computadora y Redes Neuronales (Clase 1)](https://www.youtube.com/watch?v=WRSHR33rxSU)
- [What are Convolutional Neural Networks (CNNs)?](https://www.youtube.com/watch?v=QzY57FaENXg)
- [Neural Networks Part 8: Image Classification with Convolutional Neural Networks (CNNs)](https://www.youtube.com/watch?v=HGwBXDKFk9I)
- [C4W1L01 Computer Vision](https://www.youtube.com/watch?v=ArPaAX_PhIs)
- [Convolutional Neural Networks Explained (CNN Visualized)](https://www.youtube.com/watch?v=pj9-rr1wDhM)
- [But what is a convolution?](https://www.youtube.com/watch?v=KuXjwB4LzSA)
- [Convolutional Neural Networks (CNNs) explained](https://www.youtube.com/watch?v=YRhxdVk_sIs)
