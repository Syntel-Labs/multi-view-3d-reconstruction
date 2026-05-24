"""remove_background.py — Eliminar fondo de imágenes antes del pipeline SfM.

Uso como script standalone:
    python remove_background.py data/controlgamecube/images/ --output data/controlgamecube/images_clean/

Uso como módulo dentro del pipeline (en preprocess.py):
    from remove_background import remove_background_grabcut
    img_clean = remove_background_grabcut(img_bgr)
"""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np


# ---------------------------------------------------------------------------
# Parámetros GrabCut — ajusta si el recorte no es preciso
# ---------------------------------------------------------------------------

# Margen desde cada borde como fracción de la imagen (0.08 = 8%).
# Si GrabCut corta partes del objeto: bájalo (ej. 0.04).
# Si deja demasiado fondo: súbelo (ej. 0.12).
_MARGIN = 0.08

# Iteraciones de GrabCut: más = más preciso, más lento.
_GRABCUT_ITERS = 10

# Tamaño del kernel morfológico para limpiar la máscara.
# Más grande = rellena huecos mayores pero puede unir objetos separados.
_KERNEL_SIZE = 15


def remove_background_grabcut(
    img_bgr: np.ndarray,
    margin: float = _MARGIN,
    grabcut_iters: int = _GRABCUT_ITERS,
    kernel_size: int = _KERNEL_SIZE,
    bg_color: tuple[int, int, int] = (0, 0, 0),
) -> tuple[np.ndarray, np.ndarray]:
    """Segmentar el objeto central y reemplazar el fondo con un color sólido.

    Usa GrabCut con un rect centrado que asume que el objeto de interés
    ocupa la región central de la imagen (válido para fotos de objeto sobre
    base giratoria, como el dataset controlgamecube).

    Args:
        img_bgr: Imagen BGR leída con cv2.imread.
        margin: Fracción del borde a excluir del rect inicial (default 0.08).
        grabcut_iters: Iteraciones de GrabCut (default 10).
        kernel_size: Tamaño del kernel morfológico para limpiar máscara.
        bg_color: Color BGR del fondo resultante (default negro (0,0,0)).

    Returns:
        Tupla (img_result, fg_mask) donde:
        - img_result: imagen BGR con fondo reemplazado por bg_color.
        - fg_mask: máscara uint8 (255=objeto, 0=fondo).
    """
    h, w = img_bgr.shape[:2]

    mask = np.zeros((h, w), np.uint8)
    bgd_model = np.zeros((1, 65), np.float64)
    fgd_model = np.zeros((1, 65), np.float64)

    # Rect central: el objeto debe estar dentro de este rectángulo
    mx = int(w * margin)
    my = int(h * margin)
    rect = (mx, my, w - 2 * mx, h - 2 * my)

    cv2.grabCut(
        img_bgr, mask, rect,
        bgd_model, fgd_model,
        iterCount=grabcut_iters,
        mode=cv2.GC_INIT_WITH_RECT,
    )

    # Probable foreground + foreground definitivo → objeto
    fg_mask = np.where(
        (mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0
    ).astype(np.uint8)

    # Limpieza morfológica:
    # - CLOSE: rellena huecos dentro del objeto (sombras, zonas oscuras)
    # - OPEN: elimina islas pequeñas de ruido en el fondo
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
    fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel, iterations=3)
    fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN,  kernel, iterations=1)

    # Aplicar máscara
    result = img_bgr.copy()
    result[fg_mask == 0] = bg_color

    return result, fg_mask


def process_folder(
    input_dir: Path,
    output_dir: Path,
    margin: float = _MARGIN,
    preview: bool = False,
    extensions: tuple[str, ...] = (".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"),
) -> list[Path]:
    """Procesar todas las imágenes de una carpeta y guardar en output_dir.

    Args:
        input_dir: Carpeta con las imágenes originales del dataset.
        output_dir: Carpeta destino para las imágenes con fondo removido.
        margin: Margen de GrabCut (ver remove_background_grabcut).
        preview: Si True, guarda también un collage original|resultado para revisar.
        extensions: Extensiones de archivo a procesar.

    Returns:
        Lista de rutas de las imágenes procesadas guardadas en output_dir.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    if preview:
        preview_dir = output_dir / "previews"
        preview_dir.mkdir(exist_ok=True)

    image_paths = sorted(
        p for p in input_dir.iterdir() if p.suffix in extensions
    )

    if not image_paths:
        raise FileNotFoundError(
            f"No se encontraron imágenes en {input_dir}. "
            f"Extensiones buscadas: {extensions}"
        )

    print(f"Procesando {len(image_paths)} imágenes de {input_dir} → {output_dir}")
    processed: list[Path] = []

    for idx, img_path in enumerate(image_paths):
        img_bgr = cv2.imread(str(img_path))
        if img_bgr is None:
            print(f"  [{idx+1}/{len(image_paths)}] SKIP — no se pudo leer: {img_path.name}")
            continue

        try:
            result, fg_mask = remove_background_grabcut(img_bgr, margin=margin)
        except cv2.error as e:
            print(f"  [{idx+1}/{len(image_paths)}] ERROR GrabCut en {img_path.name}: {e}")
            continue

        # Guardar imagen procesada con el mismo nombre
        out_path = output_dir / img_path.name
        cv2.imwrite(str(out_path), result, [cv2.IMWRITE_JPEG_QUALITY, 95])
        processed.append(out_path)

        # Cobertura del objeto en la imagen
        coverage = float(np.sum(fg_mask == 255)) / fg_mask.size * 100

        print(
            f"  [{idx+1}/{len(image_paths)}] {img_path.name} "
            f"→ objeto {coverage:.1f}% de la imagen"
        )

        # Collage opcional para revisión visual
        if preview:
            h, w = img_bgr.shape[:2]
            # Reducir a 640px de ancho para previews manejables
            scale = 640 / w
            small_orig = cv2.resize(img_bgr, (640, int(h * scale)))
            small_res  = cv2.resize(result,  (640, int(h * scale)))
            # Dibujar máscara en rojo semitransparente sobre original
            mask_vis = cv2.cvtColor(
                cv2.resize(fg_mask, (640, int(h * scale))), cv2.COLOR_GRAY2BGR
            )
            mask_vis[:, :, 0] = 0   # quitar canal azul y verde → solo rojo
            mask_vis[:, :, 1] = 0
            overlay = cv2.addWeighted(small_orig, 0.6, mask_vis, 0.4, 0)
            collage = np.hstack([small_orig, overlay, small_res])
            preview_path = preview_dir / (img_path.stem + "_preview.jpg")
            cv2.imwrite(str(preview_path), collage, [cv2.IMWRITE_JPEG_QUALITY, 88])

    print(f"\nListo: {len(processed)}/{len(image_paths)} imágenes guardadas en {output_dir}")
    return processed


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Quitar fondo de imágenes para el pipeline SfM (GrabCut).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Carpeta con las imágenes originales del dataset.",
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="Carpeta destino. Por defecto: <input>_clean/",
    )
    parser.add_argument(
        "--margin", "-m",
        type=float,
        default=_MARGIN,
        help=(
            "Fracción del borde excluida del rect inicial de GrabCut. "
            "Baja si corta el objeto, sube si deja demasiado fondo."
        ),
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Guardar collages original|máscara|resultado en output/previews/ para revisión.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    input_dir: Path = args.input.resolve()

    if not input_dir.exists():
        raise SystemExit(f"Error: la carpeta de entrada no existe: {input_dir}")

    output_dir = args.output.resolve() if args.output else input_dir.parent / (input_dir.name + "_clean")

    process_folder(
        input_dir=input_dir,
        output_dir=output_dir,
        margin=args.margin,
        preview=args.preview,
    )


if __name__ == "__main__":
    main()
