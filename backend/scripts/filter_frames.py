"""
filter_frames.py — Selecciona frames con suficiente variacion visual.

Uso:
    python filter_frames.py --input frames/ --output frames_filtered/ --threshold 0.02
    python filter_frames.py --input frames/ --output frames_filtered/ --target 40

Modos:
    --threshold  : descarta un frame si el cambio vs el anterior es menor a este valor (0.0-1.0)
    --target N   : elige automaticamente el threshold para quedarse con ~N frames
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import cv2
import numpy as np


def frame_diff(img_a: np.ndarray, img_b: np.ndarray) -> float:
    """Diferencia media absoluta normalizada entre dos frames en escala de grises."""
    gray_a = cv2.cvtColor(img_a, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
    gray_b = cv2.cvtColor(img_b, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
    return float(np.mean(np.abs(gray_a - gray_b)))


def load_sorted_images(folder: Path) -> list[Path]:
    exts = {".jpg", ".jpeg", ".png", ".bmp"}
    paths = sorted([p for p in folder.iterdir() if p.suffix.lower() in exts])
    if not paths:
        raise FileNotFoundError(f"No se encontraron imágenes en {folder}")
    return paths


def select_frames(paths: list[Path], threshold: float, verbose: bool = True) -> list[Path]:
    """Seleccionar frames donde el cambio vs el último aceptado supera el threshold."""
    selected = [paths[0]]
    last_img = cv2.imread(str(paths[0]))

    diffs = []
    for path in paths[1:]:
        img = cv2.imread(str(path))
        if img is None:
            continue
        diff = frame_diff(last_img, img)
        diffs.append((path, diff))
        if diff >= threshold:
            selected.append(path)
            last_img = img

    if verbose:
        all_diffs = [d for _, d in diffs]
        print(f"\n  Total frames analizados : {len(paths)}")
        print(f"  Threshold usado         : {threshold:.4f}")
        print(f"  Frames seleccionados    : {len(selected)}")
        print(f"  Diff media              : {np.mean(all_diffs):.4f}")
        print(f"  Diff min                : {np.min(all_diffs):.4f}")
        print(f"  Diff max                : {np.max(all_diffs):.4f}")

    return selected


def find_threshold_for_target(paths: list[Path], target: int) -> float:
    """Búsqueda binaria del threshold que produce ~target frames."""
    lo, hi = 0.001, 0.5
    for _ in range(30):
        mid = (lo + hi) / 2.0
        selected = select_frames(paths, mid, verbose=False)
        if len(selected) > target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def main() -> None:
    parser = argparse.ArgumentParser(description="Filtrar frames por variación visual")
    parser.add_argument("--input",  required=True, help="Carpeta con frames originales")
    parser.add_argument("--output", required=True, help="Carpeta destino para frames filtrados")
    parser.add_argument("--threshold", type=float, default=None,
                        help="Umbral de diferencia (0.0-1.0). Default: auto por --target")
    parser.add_argument("--target", type=int, default=40,
                        help="Número aproximado de frames deseados (default: 40)")
    parser.add_argument("--copy", action="store_true",
                        help="Copiar archivos en vez de solo listarlos")
    args = parser.parse_args()

    input_dir  = Path(args.input)
    output_dir = Path(args.output)

    print(f"Cargando imágenes desde: {input_dir}")
    paths = load_sorted_images(input_dir)
    print(f"Encontradas {len(paths)} imágenes")

    if args.threshold is not None:
        threshold = args.threshold
        print(f"\nUsando threshold manual: {threshold:.4f}")
    else:
        print(f"\nBuscando threshold para ~{args.target} frames...")
        threshold = find_threshold_for_target(paths, args.target)
        print(f"Threshold encontrado: {threshold:.4f}")

    selected = select_frames(paths, threshold, verbose=True)

    if args.copy:
        output_dir.mkdir(parents=True, exist_ok=True)
        for i, src in enumerate(selected):
            dst = output_dir / f"frame_{i:04d}{src.suffix}"
            shutil.copy2(src, dst)
        print(f"\nFrames copiados a: {output_dir}")
    else:
        print("\nFrames seleccionados (usa --copy para guardarlos):")
        for p in selected:
            print(f"  {p.name}")


if __name__ == "__main__":
    main()
