# Visión por Computadora – Semana 3: Transformadas y Morfología

## Introducción al módulo

En esta semana damos un salto conceptual clave: pasamos del **Dominio Espacial** al **Dominio de la Frecuencia**. Hasta ahora, todas las operaciones se realizaban directamente sobre los píxeles y sus vecinos; sin embargo, muchos problemas reales —como el ruido periódico o las texturas repetitivas— no se comprenden ni se resuelven adecuadamente en ese dominio.

A través de la **Transformada Discreta de Fourier (DFT)** y su versión eficiente, la **FFT**, aprenderemos a representar una imagen según sus componentes de frecuencia. Esto nos permitirá entender por qué la convolución espacial puede transformarse en una simple multiplicación en frecuencia, y cómo diseñar **filtros globales** capaces de eliminar ruido estructurado, aislar patrones o suprimir texturas completas, algo imposible con filtros locales tradicionales.

En paralelo, introduciremos la **Morfología Matemática**, un enfoque **no lineal** basado en la forma y la estructura de los objetos dentro de una imagen. Mediante el uso de **elementos estructurantes**, estudiaremos operaciones fundamentales como **erosión**, **dilatación**, **apertura** y **cierre**, esenciales para limpiar imágenes binarias, corregir defectos geométricos, separar regiones conectadas y preparar máscaras para tareas de segmentación y reconocimiento.

Esta semana conecta directamente el análisis matemático con aplicaciones industriales reales, sentando las bases para pipelines robustos de visión por computadora y sistemas de inteligencia artificial visual.

## Transformadas y Morfología en Visión por Computadora

En las semanas anteriores, las imágenes se analizaron como **conjuntos de píxeles independientes** en el dominio espacial. En esta etapa, el enfoque cambia: una imagen se interpreta como una **señal**, lo que permite describirla en términos de **frecuencias** y **formas**. Este cambio habilita herramientas más potentes para tratar ruido complejo, texturas repetitivas y estructuras geométricas que no pueden resolverse eficientemente con filtros locales.

## Dominio Espacial vs. Dominio Frecuencial

En el **dominio espacial**, una imagen se representa como una matriz ( f(x,y) ) donde cada píxel posee una intensidad o color. Las operaciones se realizan píxel a píxel o sobre vecindades locales, lo que resulta intuitivo pero computacionalmente costoso para kernels grandes y poco efectivo frente a ruido estructurado.

El **dominio frecuencial** describe la imagen como una combinación de ondas sinusoidales. Aquí, lo que se analiza no es el valor absoluto del píxel, sino la **tasa de cambio de intensidad**:

- **Frecuencias bajas**: regiones planas y homogéneas, donde la información semántica principal suele residir.
- **Frecuencias altas**: bordes, detalles finos y ruido.

Este dominio permite **separar el ruido de la estructura** y realizar filtrado global de manera eficiente, algo crítico cuando se requiere mantener buena resolución y lidiar con ruido complejo.

## Transformada Discreta de Fourier (DFT)

La **DFT** toma como entrada una imagen en el dominio espacial y la transforma en una representación en frecuencia ( F(u,v) ). Matemáticamente, la señal se descompone en la suma de senos y cosenos con distintas amplitudes y orientaciones.

La salida de la DFT es **compleja** y se divide en:

- **Magnitud**: indica cuánta energía o “cuánto borde” existe en una frecuencia.
- **Fase**: codifica la **estructura geométrica** y la localización espacial.

El **espectro de magnitud** permite visualizar la distribución de frecuencias. El centro del espectro corresponde al **componente DC**, ( F(0,0) ), que representa el brillo promedio de la imagen. A medida que se avanza hacia las regiones externas, aparecen las frecuencias altas asociadas a bordes y detalles. Puntos brillantes específicos indican patrones periódicos con una orientación definida.

Magnitud y fase **no son separables sin pérdida**: la magnitud dice cuánto hay, la fase dice dónde está.

## FFT y Motivación Computacional

La DFT directa es computacionalmente costosa. La **Transformada Rápida de Fourier (FFT)** es un algoritmo optimizado que reduce drásticamente la complejidad, permitiendo aplicar transformadas incluso en imágenes grandes. Esto es clave para análisis de frecuencia en tiempo razonable y para evitar los métodos espaciales iterativos vistos anteriormente, que escalan mal con el tamaño del kernel.

## Teorema de la Convolución y Filtrado en Frecuencia

El **Teorema de la Convolución** establece que:

$$
f(x,y) * h(x,y) ;\longleftrightarrow; F(u,v)\cdot H(u,v)
$$

Esto significa que una convolución costosa en el dominio espacial se convierte en una **multiplicación simple en frecuencia**. El proceso general es:

1. FFT de la imagen
2. Multiplicación por un filtro ( H(u,v) )
3. Transformada inversa (IFFT)

Con kernels grandes, este enfoque es mucho más eficiente.

### Tipos de filtros

- **Filtro paso bajo**: valores altos en el centro y ceros afuera → elimina frecuencias altas (blur).
- **Filtro paso alto**: ceros en el centro y unos en la periferia → elimina bajas frecuencias y resalta bordes.

El uso de Fourier depende del tamaño del kernel: para kernels pequeños no es necesario; para kernels grandes o filtrado global, es indispensable.

## Morfología Matemática

La **morfología matemática** es un enfoque **no lineal** basado en la **teoría de conjuntos** y el análisis de formas. Opera principalmente sobre imágenes binarias, aunque puede extenderse a escala de grises.

- **Imagen de entrada**: conjunto $A$
- **Elemento estructurante (SE)**: kernel $B$ que actúa como una sonda
- **Operación lógica**: no hay multiplicaciones ni sumas, sino intersecciones y ajustes

El elemento estructurante se traslada sobre toda la imagen:

- **Fit (ajuste)**: todos los píxeles del SE coinciden con el objeto
- **Hit (intersección)**: al menos un píxel del SE toca el objeto

## Dilatación

La **dilatación** expande las regiones brillantes. Actúa como un **filtro de máximo local**:

- Si algún píxel del SE intersecta el objeto, el píxel central se activa.
- Engrosa líneas, rellena huecos pequeños y conecta regiones cercanas.
- Efecto secundario: pérdida de detalle fino y expansión excesiva.

La forma y tamaño del SE determinan cuánto y cómo crece el objeto (cuadrado, disco, línea, etc.).

## Erosión

La **erosión** es la operación opuesta:

- Reduce las regiones brillantes.
- Actúa como un **mínimo local**.
- El píxel central se conserva solo si el SE cabe completamente dentro del objeto.

Es eficaz para eliminar ruido tipo **sal** (puntos blancos aislados), pero también puede romper estructuras delgadas.

## Apertura y Cierre

Estas operaciones se usan **en combinación**, no de forma pura.

- **Apertura**: erosión seguida de dilatación
  Elimina ruido brillante pequeño y preserva la forma general del objeto. Es menos destructiva que la erosión sola.

- **Cierre**: dilatación seguida de erosión
  Rellena agujeros, grietas y desconexiones internas. Ideal para ruido tipo **pimienta**.

El **orden importa** y estas operaciones son **no conmutativas**. Además, presentan **idempotencia**: aplicarlas múltiples veces no cambia el resultado tras cierto punto.

## Rol de Fourier y Morfología en el Pipeline

- **Fourier**: manipulación **global** de la imagen, basada en frecuencia.
- **Filtrado**: modificación de la magnitud para suavizar o realzar.
- **Morfología**: manipulación **local** de formas y estructuras.

Ninguna de estas técnicas identifica por sí sola qué es un objeto; preparan la imagen para etapas posteriores como **detección de características**, **descriptores** y **matching**, que se abordarán en las siguientes semanas.

## Expansión Matemática

### Transformada Discreta de Fourier (DFT)

Sea una imagen en escala de grises representada como una función discreta
$f(x,y)$ de tamaño $M \times N$.

La **Transformada Discreta de Fourier bidimensional** se define como:

$$
F(u,v)=\sum_{x=0}^{M-1}\sum_{y=0}^{N-1} f(x,y),e^{-j2\pi\left(\frac{ux}{M}+\frac{vy}{N}\right)}
$$

donde:

- $f(x,y)$ es la intensidad del píxel en el dominio espacial
- $F(u,v)$ es la representación en el dominio frecuencial
- $(u,v)$ son las frecuencias horizontal y vertical
- $j$ es la unidad imaginaria

La transformada inversa (IDFT) es:

$$
f(x,y)=\frac{1}{MN}\sum_{u=0}^{M-1}\sum_{v=0}^{N-1} F(u,v),e^{j2\pi\left(\frac{ux}{M}+\frac{vy}{N}\right)}
$$

### Magnitud y Fase

El resultado $F(u,v)$ es complejo y se descompone en:

- **Magnitud**:
  $$
  |F(u,v)|=\sqrt{\Re(F(u,v))^2+\Im(F(u,v))^2}
  $$

- **Fase**:
  $$
  \phi(u,v)=\arctan\left(\frac{\Im(F(u,v))}{\Re(F(u,v))}\right)
  $$

La magnitud indica **cuánta energía** existe en una frecuencia, mientras que la fase contiene la **estructura geométrica** de la imagen. Eliminar la fase implica perder la forma del contenido.

### Componente DC

El componente DC se encuentra en:

$$
F(0,0)=\sum_{x=0}^{M-1}\sum_{y=0}^{N-1} f(x,y)
$$

y representa el **brillo promedio global** de la imagen. Por esta razón aparece como el punto más brillante en el centro del espectro tras aplicar el desplazamiento del espectro (FFT shift).

### Teorema de la Convolución

Para una imagen $f(x,y)$ y un kernel $h(x,y)$:

$$
f(x,y)*h(x,y);\Longleftrightarrow;F(u,v)\cdot H(u,v)
$$

Esto demuestra que:

- La convolución espacial se convierte en multiplicación en frecuencia
- El filtrado global es computacionalmente más eficiente usando FFT

### Filtros en Frecuencia

- **Filtro paso bajo ideal**:
  $$
  H(u,v)=
  \begin{cases}
  1 & \text{si } \sqrt{u^2+v^2} \le D_0 \
  0 & \text{en otro caso}
  \end{cases}
  $$

- **Filtro paso alto ideal**:
  $$
  H(u,v)=1-\text{LPF}(u,v)
  $$

donde $D_0$ es la frecuencia de corte.

### Morfología Matemática: Definiciones Formales

Sea $A$ la imagen binaria y $B$ el elemento estructurante.

- **Erosión**:
  $$
  A \ominus B={z\mid B_z \subseteq A}
  $$

Intuición: el SE debe **encajar completamente** en el objeto.

- **Dilatación**:
  $$
  A \oplus B={z\mid \hat{B}_z \cap A \neq \varnothing}
  $$

Intuición: basta con que el SE **toque** el objeto.

### Apertura y Cierre

- **Apertura**:
  $$
  A \circ B=(A \ominus B)\oplus B
  $$

Elimina ruido pequeño brillante y preserva la forma principal.

- **Cierre**:
  $$
  A \bullet B=(A \oplus B)\ominus B
  $$

Rellena agujeros y grietas internas.

Estas operaciones **no son conmutativas** y cumplen **idempotencia**:

$$
(A \circ B)\circ B = A \circ B
$$

$$
(A \bullet B)\bullet B = A \bullet B
$$

## Transformada de Fourier y Dominio de la Frecuencia

### Fundamentos teóricos

- **[Explicación: La transformada de Fourier discreta](https://news.mit.edu/2009/explained-fourier)**
  Introducción conceptual clara al significado físico y matemático de la DFT.

- **[Comprensión de la DFT: una guía para principiantes sobre la transformada de Fourier discreta](https://wraycastle.com/es/blogs/knowledge-base/dft-discrete-fourier-transform)**
  Explicación paso a paso orientada a principiantes.

- **[Understand the convolution theorem](https://peterbbryan.medium.com/understand-the-convolution-theorem-ff039caa745e)**
  Relación clave entre convolución espacial y multiplicación en frecuencia.

- **[The convolution theorem and its applications](https://www-structmed.cimr.cam.ac.uk/Course/Convolution/convolution.html)**
  Enfoque más formal y matemático del teorema de la convolución.

### Videos explicativos (DFT y FFT)

- **[Transformada Discreta de Fourier](https://www.youtube.com/watch?v=HSNQgNcI2V4)**
- **[Transformada Discreta de Fourier | UPV](https://www.youtube.com/watch?v=ysjbvYvHZOY)**
- **[TRANSFORMADA DE FOURIER en 5 TRUCOS](https://www.youtube.com/watch?v=EOhg348BHc8)**
- **[Pero, ¿qué es la transformada de Fourier? Una introducción visual](https://www.youtube.com/watch?v=spUNpyF58BY)**

### Fourier y Convolución

- **[Convolution and the Fourier Transform explained visually](https://www.youtube.com/watch?v=9i6aDdQ9FTQ)**
  Visualización intuitiva del vínculo entre ambos dominios.

- **[The Fast Fourier Transform (FFT): Most Ingenious Algorithm Ever?](https://www.youtube.com/watch?v=h7apO7q16V0)**
  Contexto histórico y computacional de la FFT.

- **[Understanding the Discrete Fourier Transform and the FFT](https://www.youtube.com/watch?v=QmgJmh2I3Fw)**
  Comparación clara entre DFT y FFT.

## Morfología Matemática

### Operaciones fundamentales

- **[OpenCV: Dilatación y erosión morfológica](https://medium.com/@sasaniperera/opencv-morphological-dilation-and-erosion-fab65c29efb3)**
  Implementación práctica con OpenCV.

- **[Erosión y dilatación en el procesamiento de imágenes](https://www.scaler.com/topics/erosion-and-dilation-in-image-processing/)**
  Explicación conceptual de ambas operaciones.

- **[Diferencia entre dilatación y erosión](https://www.geeksforgeeks.org/computer-vision/difference-between-dilation-and-erosion/)**
  Comparación directa y casos de uso.

### Operaciones compuestas

- **[Apertura (Operación Morfológica)](https://medium.com/@anshul16/opening-morphological-operation-image-processing-bbdbe210e3bc)**
  Uso de apertura para eliminación de ruido.

- **[3.7 filtros morfológicos](https://www.youtube.com/watch?v=mYqxPM-f5Rg)**
  Visión general de filtros morfológicos.

- **[Operaciones morfológicas](https://www.youtube.com/watch?v=f2PiVt_pq8k)**
  Resumen visual de erosión, dilatación, apertura y cierre.

- **[Opening Followed by Closing](https://www.youtube.com/watch?v=1owu136z1zI)**
  Uso secuencial de operaciones para refinamiento de máscaras.
