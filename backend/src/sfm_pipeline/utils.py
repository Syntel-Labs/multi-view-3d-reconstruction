"""Utilidades geometricas y de I/O compartidas por todos los modulos del pipeline.

Ninguna funcion aqui tiene efectos secundarios mas alla de leer/escribir archivos.
Importar segun necesidad: no importar el modulo completo para no arrastrar dependencias.
"""

from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np


# ---------------------------------------------------------------------------
# I/O de imagenes
# ---------------------------------------------------------------------------

def load_image(path: str | Path, grayscale: bool = False) -> np.ndarray:
    """Cargar una imagen desde disco.

    Args:
        path:      ruta al archivo (jpg, png, etc.).
        grayscale: si True devuelve array (H, W) uint8;
                   si False devuelve (H, W, 3) BGR uint8.

    Returns:
        Array numpy con la imagen.

    Raises:
        FileNotFoundError: si el archivo no existe.
        ValueError:        si OpenCV no puede leer el archivo.

    Nota sobre color vs grises
    --------------------------
    Los modulos de la persona B (geometry, triangulation, sfm, metrics) trabajan
    exclusivamente con coordenadas 2D de keypoints (arrays float32), nunca con
    pixeles de imagen directamente. Por eso el color o grises de la imagen NO
    afecta la precision de F, E, triangulacion ni reproyeccion.

    Usar grayscale=True solo cuando se vayan a visualizar matches o dibujar
    keypoints sobre la imagen, o cuando se quiera ahorrar memoria al cargar
    muchas imagenes de un dataset grande.

    La conversion a grises para deteccion SIFT/ORB la hace la persona A en
    preprocess.py; la persona B no necesita hacerla.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Imagen no encontrada: {path}")
    flag = cv2.IMREAD_GRAYSCALE if grayscale else cv2.IMREAD_COLOR
    img = cv2.imread(str(p), flag)
    if img is None:
        raise ValueError(f"OpenCV no pudo leer la imagen: {path}")
    return img


def list_images(folder: str | Path, exts: tuple[str, ...] = (".jpg", ".jpeg", ".png")) -> list[Path]:
    """Listar imagenes de una carpeta ordenadas por nombre.

    Args:
        folder: ruta a la carpeta (tipicamente data/<dataset>/images/).
        exts:   extensiones aceptadas, en minusculas.

    Returns:
        Lista de Path ordenada lexicograficamente.
    """
    folder = Path(folder)
    paths = sorted(p for p in folder.iterdir() if p.suffix.lower() in exts)
    return paths


# ---------------------------------------------------------------------------
# I/O de intrinsics
# ---------------------------------------------------------------------------

def load_intrinsics(path: str | Path) -> np.ndarray:
    """Cargar la matriz intrinseca K desde un intrinsics.json.

    El schema del archivo esta definido en docs/contracts/intrinsics-json.md.

    Args:
        path: ruta al intrinsics.json del dataset.

    Returns:
        K: matriz intrinseca (3, 3) float64.

    Raises:
        FileNotFoundError: si el archivo no existe.
        ValueError:        si focal_length_px es 0 (dataset sin completar).
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"intrinsics.json no encontrado: {path}")

    with p.open() as f:
        data = json.load(f)

    fx = float(data["focal_length_px"])
    if fx == 0.0:
        raise ValueError(
            f"focal_length_px es 0 en {path}. "
            "Completar intrinsics.json con los datos del dispositivo."
        )

    cx, cy = data["principal_point_px"]
    K = np.array(
        [[fx, 0.0, float(cx)], [0.0, fx, float(cy)], [0.0, 0.0, 1.0]],
        dtype=np.float64,
    )
    return K


def focal_from_exif_35mm(focal_35mm: float, image_width_px: int) -> float:
    """Estimar focal length en pixeles desde el equivalente 35mm del EXIF.

    Formula: f_px = f_35mm * W_px / 36
    (el sensor de referencia 35mm mide 36 mm de ancho)

    Args:
        focal_35mm:     focal equivalente en mm (tag EXIF FocalLengthIn35mmFilm).
        image_width_px: ancho de la imagen en pixeles.

    Returns:
        Focal length estimada en pixeles.
    """
    return focal_35mm * image_width_px / 36.0


# ---------------------------------------------------------------------------
# Construccion de matrices de camara
# ---------------------------------------------------------------------------

def build_projection_matrix(K: np.ndarray, R: np.ndarray, t: np.ndarray) -> np.ndarray:
    """Construir la matriz de proyeccion P = K [R | t].

    Args:
        K: matriz intrinseca (3, 3).
        R: matriz de rotacion (3, 3).
        t: vector de traslacion (3,) o (3, 1).

    Returns:
        P: matriz de proyeccion (3, 4).
    """
    Rt = np.hstack([R, t.reshape(3, 1)])
    return K @ Rt


def camera_center(R: np.ndarray, t: np.ndarray) -> np.ndarray:
    """Calcular el centro optico de la camara en coordenadas del mundo.

    C = -R^T t

    Args:
        R: matriz de rotacion (3, 3).
        t: vector de traslacion (3,) o (3, 1).

    Returns:
        C: centro optico (3,).
    """
    return (-R.T @ t.reshape(3, 1)).ravel()


# ---------------------------------------------------------------------------
# Conversion de coordenadas
# ---------------------------------------------------------------------------

def to_homogeneous(pts: np.ndarray) -> np.ndarray:
    """Agregar columna de unos para convertir a coordenadas homogeneas.

    Args:
        pts: (n, d) array de puntos cartesianos.

    Returns:
        (n, d+1) array homogeneo.
    """
    ones = np.ones((pts.shape[0], 1), dtype=pts.dtype)
    return np.hstack([pts, ones])


def from_homogeneous(pts: np.ndarray) -> np.ndarray:
    """Dividir por la ultima coordenada y descartar la columna homogenea.

    Args:
        pts: (n, d+1) o (d+1, n) array homogeneo.

    Returns:
        (n, d) array cartesiano.
    """
    if pts.shape[0] < pts.shape[1]:
        # Formato columnas (4, n) — tipico de triangulatePoints
        pts = pts.T
    return (pts[:, :-1] / pts[:, -1:]).astype(np.float64)


# ---------------------------------------------------------------------------
# Filtros geometricos
# ---------------------------------------------------------------------------

def filter_cheirality(
    pts3d: np.ndarray,
    R1: np.ndarray,
    t1: np.ndarray,
    R2: np.ndarray,
    t2: np.ndarray,
) -> np.ndarray:
    """Devolver mascara booleana de puntos que estan delante de ambas camaras.

    Un punto X esta delante de una camara si su coordenada Z en el sistema
    de la camara es positiva: r3 · (X - C) > 0.

    Args:
        pts3d: (n, 3) array de puntos 3D.
        R1, t1: pose de la camara 1.
        R2, t2: pose de la camara 2.

    Returns:
        Mascara booleana (n,).
    """
    pts_cam1 = (R1 @ pts3d.T + t1.reshape(3, 1)).T
    pts_cam2 = (R2 @ pts3d.T + t2.reshape(3, 1)).T
    return (pts_cam1[:, 2] > 0) & (pts_cam2[:, 2] > 0)


def filter_max_depth(pts3d: np.ndarray, max_depth: float = 100.0) -> np.ndarray:
    """Mascara booleana de puntos con profundidad Z menor al limite.

    Filtra outliers lejanos que aparecen cuando dos rayos son casi paralelos
    (baseline pequeno o angulo de convergencia cercano a cero).

    Args:
        pts3d:     (n, 3) array de puntos 3D en coordenadas de la primera camara.
        max_depth: profundidad maxima aceptable en unidades de la escena.

    Returns:
        Mascara booleana (n,).
    """
    return pts3d[:, 2] < max_depth


# ---------------------------------------------------------------------------
# Metricas geometricas
# ---------------------------------------------------------------------------

def reprojection_errors(
    pts3d: np.ndarray,
    pts2d: np.ndarray,
    K: np.ndarray,
    R: np.ndarray,
    t: np.ndarray,
) -> np.ndarray:
    """Calcular el error de reproyeccion en pixeles para cada punto.

    Args:
        pts3d: (n, 3) puntos 3D.
        pts2d: (n, 2) observaciones 2D correspondientes.
        K:     matriz intrinseca (3, 3).
        R:     matriz de rotacion (3, 3).
        t:     vector de traslacion (3,) o (3, 1).

    Returns:
        errors: (n,) array de errores en pixeles.
    """
    P = build_projection_matrix(K, R, t)
    pts_h = to_homogeneous(pts3d).T       # (4, n)
    proj = P @ pts_h                       # (3, n)
    proj2d = (proj[:2] / proj[2]).T        # (n, 2)
    return np.linalg.norm(pts2d - proj2d, axis=1).astype(np.float64)


def rotation_angle_deg(R1: np.ndarray, R2: np.ndarray) -> float:
    """Angulo en grados entre dos matrices de rotacion.

    Util para comparar R estimada con ground truth en validaciones.

    Args:
        R1, R2: matrices de rotacion (3, 3).

    Returns:
        Angulo en grados en [0, 180].
    """
    R_diff = R1 @ R2.T
    cos_angle = float(np.clip((np.trace(R_diff) - 1.0) / 2.0, -1.0, 1.0))
    return float(np.degrees(np.arccos(cos_angle)))
