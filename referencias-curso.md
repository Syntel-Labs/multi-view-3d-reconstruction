# Referencias del curso aplicables al proyecto

Mapeo de las anotaciones de clase (semanas 1 a 14) y de los laboratorios ya entregados que sirven como base teorica y como codigo reciclable para el pipeline de Structure from Motion.

Documentos relacionados:

- [plan.md](./plan.md)
- [idea-1-reconstruccion-3d.md](./idea-1-reconstruccion-3d.md)
- [Proyecto Final.pdf](./Proyecto%20Final.pdf)

## Anotaciones de clase

Relevancia para el core de SfM (clasica, sin extras). Las marcadas como **core** son la base teorica que se cita en el documento final. Las marcadas como opcionales pueden mencionarse pero no son indispensables.

| Semana | Tema | Relevancia | Para que sirve en el proyecto |
| :--- | :--- | :--- | :--- |
| [Semana 1](../../../anotaciones/semana1.md) | Imagen como tensor, BGR vs RGB, HSV, Lab, tipos de datos | Opcional | Justificar el preprocesamiento (`uint8` vs `float32`), cuidar la trampa BGR de OpenCV al cargar fotos. |
| [Semana 2](../../../anotaciones/semana2.md) | Convolucion, padding, filtro Gaussiano, Sobel, Canny | Core | Preprocesamiento de cada foto: Gaussiano para reducir ruido antes de SIFT/ORB. |
| [Semana 3](../../../anotaciones/semana3.md) | Fourier (DFT/FFT), morfologia matematica | Opcional | Limpieza de fondo en datasets controlados antes del matching. No critico. |
| [Semana 4](../../../anotaciones/semana4.md) | Harris, SIFT, ORB, FAST, BRIEF, BFMatcher, FLANN, Lowe's ratio test, RANSAC | **Core principal** | Detector + descriptor + matching + filtrado. Todo el front del pipeline esta aqui. |
| [Semana 5](../../../anotaciones/semana5.md) | Coordenadas homogeneas, modelo pinhole, $K$, $R$, $t$, homografias, DLT, SVD, RANSAC formal | **Core principal** | Modelo de camara, estimacion de homografias y RANSAC. Justificacion de por que necesitamos $K$ para pasar de $F$ a $E$. |
| [Semana 6](../../../anotaciones/semana6.md) | Workshop de panoramas: stitching, paralaje, transicion a estereo y matriz fundamental $F$ | **Core principal** | Conexion directa: panorama exige $C_1 = C_2$, SfM exige $C_1 \neq C_2$. Aqui se introduce la condicion epipolar $x'^T F x = 0$. |
| [Semana 7](../../../anotaciones/semana7.md) (parte 1) | Vision estereo, baseline, geometria epipolar, matriz fundamental, formula $Z = fB/d$ | **Core principal** | Profundidad por triangulacion. Brecha: la semana no entra en el algoritmo de 8 puntos ni en la descomposicion de $E$, hay que complementar con bibliografia externa. |
| Semana 7 (parte 2) a 14 | CNNs, ResNet, Transfer Learning, YOLO, U-Net, Mask R-CNN, ViT | No relevante | Quedan fuera del scope del proyecto core. |

### Brechas teoricas que no cubre el curso

Hay que apoyarse en bibliografia externa (Hartley and Zisserman, OpenCV docs) para tres puntos:

1. Algoritmo de 8 puntos para estimar $F$ (la semana 6 lo menciona pero no lo desarrolla).
2. Descomposicion de la matriz esencial $E = U \Sigma V^T$ en $R$ y $t$ con verificacion de cheirality.
3. Triangulacion lineal por DLT y refinamiento iterativo del punto 3D.

## Laboratorios entregados

Mapeo del codigo ya implementado en los labs y workshops del semestre. La columna "Reusable" indica si el componente puede copiarse o adaptarse al pipeline del proyecto.

| Lab | Tema | Color o grises | Alcance | Reusable |
| :--- | :--- | :--- | :--- | :--- |
| Lab 1 | Convolucion 2D manual + kernel Gaussiano + Sobel | Grises (forzado) | Convolucion desde cero en NumPy, magnitud y direccion del gradiente | Si: `mi_convolucion`, `generar_gaussiano`, `detectar_bordes_sobel` para el preprocesamiento |
| Lab 2 | FFT + morfologia matematica | Grises y binaria | Notch filter manual, erosion, dilatacion, apertura, cierre | Solo si se usa morfologia para limpiar fondo (opcional) |
| Lab 3 | Harris, SIFT, ORB + matching | Grises | Deteccion + descriptor + BFMatcher + Lowe's ratio test 0.75 + visualizacion de inliers | **Si, base directa del front del pipeline SfM** |
| Lab 4 | Homografia DLT + RANSAC manual + stitching | Grises (features) y color (warp) | DLT con SVD normalizado, RANSAC con $N$ dinamico, refinamiento con todos los inliers | **Si**, el RANSAC y el armado de la matriz por SVD se adaptan al algoritmo de 8 puntos para $F$ |
| Lab 5 | Paralaje y limites de la homografia | No especifica | Stitching con traslacion lateral, medicion de disparidad vs profundidad real | Si, motivacion experimental para justificar el uso de SfM en lugar de panorama |
| Lab 6 | CNN con Transfer Learning (ResNet, MobileNet) | Color | Clasificacion fine-tuned | No |
| Lab 7 | CNN con Data Augmentation en radiografias | Grises | Clasificacion medica | No |
| Lab 8 | YOLO, IoU, NMS, mAP | Color | Deteccion de objetos | No |
| Lab 9 | U-Net, Mask R-CNN, YOLO en tiempo real | Color | Segmentacion e inferencia con webcam | No |
| Workshop 1 | Contraste, gamma, segmentacion HSV | Color | Operaciones puntuales en NumPy | No (solo si se hace segmentacion HSV opcional) |
| Workshop 2 | Convolucion con stride/padding + paralaje | Grises | Convolucion manual + analisis teorico de paralaje | No directamente, pero refuerza la motivacion del proyecto |

### Respuesta a las preguntas concretas

- **Color o blanco y negro**: el frontend del pipeline (Lab 1, 3, 4 y 5) trabaja en escala de grises. Es el estandar al usar SIFT/ORB y RANSAC sobre homografias. El proyecto seguira el mismo criterio: cargar las fotos en color, pero convertir a grises para detectar features. La nube de puntos final no tiene color asociado en el core (la coloracion por foto es un extra opcional, no esta en el scope).
- **Hasta donde llegaron en geometria**: el curso cubre formalmente hasta homografias 2D y RANSAC. La geometria epipolar y la matriz fundamental se mencionan en la semana 6 y 7 como transicion, pero no hay un lab dedicado. Por eso $F$, $E$, descomposicion en $R$ y $t$, y triangulacion son brecha que el proyecto debe implementar nuevo.
- **Importa el formato de entrada**: si, las fotos deben venir con EXIF para extraer la focal aproximada y construir $K$. Si la camara no expone EXIF, hay que documentar la limitacion.

## Componentes reusables priorizados

| Prioridad | Componente | Origen | Uso en el proyecto |
| :--- | :--- | :--- | :--- |
| Alta | Carga de imagen + Gaussiano + conversion a grises | Lab 1 | Preprocesamiento en `features.py` |
| Alta | SIFT/ORB + BFMatcher + Lowe's ratio test | Lab 3 | Cuerpo de `features.py` y `matching.py` |
| Alta | RANSAC manual con $N$ dinamico | Lab 4 | Adaptar a `findFundamentalMat` o usar la version de OpenCV citando el lab como referencia |
| Alta | DLT con SVD normalizado | Lab 4 | Adaptar al algoritmo de 8 puntos para $F$ y a la triangulacion |
| Media | Sobel manual | Lab 1 | Diagnostico visual de zonas con baja textura (areas problematicas) |
| Media | Medicion de disparidad por profundidad | Lab 5 | Comparativa empirica panorama vs SfM en el documento final |
| Baja | Morfologia matematica | Lab 2 | Limpieza opcional de mascaras de fondo |

## Brechas que requieren implementacion nueva

Lo siguiente no esta en ningun lab y debe escribirse desde cero o usando OpenCV directamente:

1. Construccion de $K$ desde EXIF: $f_{px} \approx f_{mm} \cdot W / s_{mm}$.
2. Algoritmo de 8 puntos para estimar $F$ con normalizacion de Hartley.
3. Conversion $E = K^T F K$ y descomposicion en $R$ y $t$ con cheirality check.
4. Triangulacion lineal por DLT (`cv2.triangulatePoints`).
5. Registro multi-vista incremental con `solvePnPRansac`.
6. Calculo del reprojection error como metrica.
7. Exportacion a `.ply`.
8. Demo web (FastAPI + Three.js).

## Recomendacion de copia al repo del proyecto

Para tener todo el material como referencia dentro del repositorio publico, se sugiere crear `docs/teoria/` con copia literal de las anotaciones relevantes:

```text
docs/
├── notas.md                     (sintesis propia para la entrega 1)
├── referencias-curso.md         (este archivo)
└── teoria/
    ├── 02-filtrado-convolucion.md   (copia de semana2.md)
    ├── 03-morfologia.md             (copia de semana3.md, opcional)
    ├── 04-features-locales.md       (copia de semana4.md)
    ├── 05-geometria-proyectiva.md   (copia de semana5.md)
    ├── 06-homografia-stitching.md   (copia de semana6.md)
    └── 07-geometria-epipolar.md     (copia de semana7.md, recortada)
```

La semana 1 no se copia (es introductoria) y de la semana 7 solo interesan las primeras secciones (vision estereo + geometria epipolar), no la parte de CNNs.

## Bibliografia complementaria sugerida para llenar las brechas

Estos enlaces ya aparecen en las anotaciones del curso y son los que cubren lo que el curso no profundiza:

- [Hartley, In defence of the 8-point algorithm](https://users.cecs.anu.edu.au/~hartley/Papers/fundamental/electronic-submission/fundamental.pdf) (citado en semana 5)
- [Marginal Notes for Hartley and Zisserman's Multiple View Geometry](https://staff.fnwi.uva.nl/l.dorst/hz/hz.pdf) (citado en semana 5)
- [Epipolar Geometry: Solving the fundamental Matrix](https://www.youtube.com/watch?v=Xmcu_XPrTho) (citado en semana 6)
- [Photogrammetry II - Epipolar Geometry and Essential Matrix](https://www.youtube.com/watch?v=vNG0uJR48XE) (citado en semana 6)
- [Estimating Fundamental Matrix - Uncalibrated Stereo](https://www.youtube.com/watch?v=izpYAwJ0Hlw) (citado en semana 6)
- [OpenCV Stereo Vision Disparity (Depth Map)](https://www.youtube.com/watch?v=5LrAhSHNIJU) (citado en semana 6)
- [COLMAP](https://colmap.github.io/) (citado en `idea-1-reconstruccion-3d.md`)
