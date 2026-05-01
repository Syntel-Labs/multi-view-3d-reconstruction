"""Script de uso unico: genera un par estereo sintetico para validar geometry.py.

Crea puntos 3D aleatorios, los proyecta con dos camaras de pose conocida,
agrega ruido gaussiano y exporta las correspondencias como .npz.
Uso: python -m scripts.synthetic_stereo
"""

import numpy as np


def build_camera(f: float, w: int, h: int) -> np.ndarray:
    """Construir matriz intrinseca K para una camara pinhole centrada."""
    return np.array(
        [[f, 0.0, w / 2.0], [0.0, f, h / 2.0], [0.0, 0.0, 1.0]],
        dtype=np.float64,
    )


def project(pts3d: np.ndarray, K: np.ndarray, R: np.ndarray, t: np.ndarray) -> np.ndarray:
    """Proyectar puntos 3D (n,3) con camara K[R|t]. Devuelve (n,2) en pixeles."""
    pts_cam = (R @ pts3d.T + t.reshape(3, 1)).T      # (n, 3)
    pts_proj = (K @ pts_cam.T).T                       # (n, 3) homogeneo
    pts_2d = pts_proj[:, :2] / pts_proj[:, 2:3]
    return pts_2d.astype(np.float32)


def generate_stereo_pair(
    n_points: int = 200,
    focal: float = 1200.0,
    width: int = 1280,
    height: int = 960,
    noise_std: float = 0.5,
    seed: int = 42,
) -> dict:
    """Generar par estereo sintetico con pose conocida.

    Camara 1: en el origen, mirando hacia +Z.
    Camara 2: trasladada 1 unidad en X y rotada 10 grados sobre Y.

    Args:
        n_points:  numero de puntos 3D en la escena
        focal:     focal length en pixeles
        width:     ancho de imagen en pixeles
        height:    alto de imagen en pixeles
        noise_std: desviacion estandar del ruido gaussiano en pixeles
        seed:      semilla para reproducibilidad

    Returns:
        Diccionario con K, R_gt, t_gt, pts3d, pts_img1, pts_img2 y mascara de visibilidad.
    """
    rng = np.random.default_rng(seed)

    K = build_camera(focal, width, height)

    # Escena: puntos frente a la camara, dispersos en un volumen
    pts3d = rng.uniform(
        low=[-1.0, -1.0, 3.0],
        high=[1.0, 1.0, 6.0],
        size=(n_points, 3),
    )

    # Camara 1: identidad
    R1 = np.eye(3)
    t1 = np.zeros((3, 1))

    # Camara 2: rotacion de 10 grados sobre Y + traslacion de 1 unidad en X
    angle = np.radians(10.0)
    R2 = np.array(
        [
            [np.cos(angle), 0.0, np.sin(angle)],
            [0.0, 1.0, 0.0],
            [-np.sin(angle), 0.0, np.cos(angle)],
        ]
    )
    t2 = np.array([[-1.0], [0.0], [0.0]])

    # Proyectar
    pts1 = project(pts3d, K, R1, t1)
    pts2 = project(pts3d, K, R2, t2)

    # Filtrar puntos visibles en ambas imagenes
    margen = 5.0
    visible = (
        (pts1[:, 0] > margen)
        & (pts1[:, 0] < width - margen)
        & (pts1[:, 1] > margen)
        & (pts1[:, 1] < height - margen)
        & (pts2[:, 0] > margen)
        & (pts2[:, 0] < width - margen)
        & (pts2[:, 1] > margen)
        & (pts2[:, 1] < height - margen)
    )

    pts3d_v = pts3d[visible]
    pts1_v = pts1[visible]
    pts2_v = pts2[visible]

    # Agregar ruido gaussiano
    if noise_std > 0:
        pts1_v = pts1_v + rng.normal(0.0, noise_std, pts1_v.shape).astype(np.float32)
        pts2_v = pts2_v + rng.normal(0.0, noise_std, pts2_v.shape).astype(np.float32)

    return {
        "K": K,
        "R_gt": R2,
        "t_gt": t2,
        "pts3d": pts3d_v,
        "pts_img1": pts1_v,
        "pts_img2": pts2_v,
        "n_visible": int(visible.sum()),
    }


def save_stereo_pair(data: dict, path: str = "data/synthetic_stereo.npz") -> None:
    """Serializar el par sintetico a un archivo .npz."""
    np.savez(
        path,
        K=data["K"],
        R_gt=data["R_gt"],
        t_gt=data["t_gt"],
        pts3d=data["pts3d"],
        pts_img1=data["pts_img1"],
        pts_img2=data["pts_img2"],
    )
    print(f"Par sintetico guardado en {path} ({data['n_visible']} puntos visibles)")


if __name__ == "__main__":
    data = generate_stereo_pair()
    save_stereo_pair(data)
    print(f"K:\n{data['K']}")
    print(f"R_gt:\n{data['R_gt']}")
    print(f"t_gt: {data['t_gt'].ravel()}")
