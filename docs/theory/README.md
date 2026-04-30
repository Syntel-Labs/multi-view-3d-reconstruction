# Teoria del curso

Copias literales de las anotaciones del catedratico relevantes al pipeline SfM. Permite que todo el equipo tenga el material citado en el documento final dentro del repo, aunque las fuentes originales vivan fuera.

## Archivos

```text
docs/theory/
├── README.md
├── 01_introduction.md             # imagenes digitales, BGR/RGB, HSV, Lab
├── 02_filtering-convolution.md    # convolucion, padding, Gaussiano, Sobel, Canny
├── 03_fourier-morphology.md       # DFT/FFT, morfologia matematica
├── 04_local-features.md           # Harris, SIFT, ORB, BFMatcher, Lowe, RANSAC
├── 05_projective-geometry.md      # coordenadas homogeneas, pinhole, K, R, t, DLT
├── 06_homography-stitching.md     # workshop panoramas, paralaje, transicion a F
└── 07_epipolar-geometry.md        # vision estereo, baseline, F, formula Z = fB/d
```

## Reglas

- Mantener el contenido lo mas fiel posible al original.
- Si se hace una sintesis propia, ponerla en `docs/lectures/` no aqui.
- Citar al final del archivo la fuente original (link o ruta a las anotaciones del catedratico).

## Mapeo a modulos

Ver [`docs/course-references.md`](../course-references.md) para el cruce semana - modulo del pipeline.
