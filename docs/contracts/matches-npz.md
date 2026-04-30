# Contrato - matches.npz

- Version: 0.1.0
- Productor: Persona A
- Consumidor: Persona B

Define el archivo intermedio que entrega A a B con los keypoints, descriptores y matches filtrados de un dataset.

## Ubicacion

```text
data/<name>/matches.npz
```

## Contenido

Archivo `.npz` (NumPy compressed) con las siguientes claves:

| Clave | Forma | Tipo | Descripcion |
| :--- | :--- | :--- | :--- |
| `image_paths` | `(N,)` | `str` | Rutas relativas a `data/<name>/images/`. |
| `keypoints_<i>` | `(N_i, 2)` | `float32` | Coordenadas `(x, y)` por imagen `i`. |
| `descriptors_<i>` | `(N_i, D)` | `float32` o `uint8` | D=128 (SIFT) o D=32 (ORB). |
| `matches_<i>_<j>` | `(M, 2)` | `int32` | Indices a keypoints de imagen i y j tras Lowe ratio test. |
| `detector` | escalar | `str` | "sift" o "orb". |
| `lowe_ratio` | escalar | `float32` | Umbral de Lowe usado (default 0.75). |

## Convenciones

- `i` es el indice de la imagen en `image_paths`.
- Solo se guardan matches para pares `(i, j)` consecutivos, salvo que se acuerde el modo all-pairs.
- Coordenadas en pixeles, origen arriba-izquierda (convencion de OpenCV).
