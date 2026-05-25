from __future__ import annotations

import argparse
import sys


def main() -> None:
    """Parsear argumentos y delegar en sfm.run_pipeline.

    Codigos de salida segun contrato cli-sfm.md:
        0 - pipeline completado.
        1 - error generico no controlado.
        2 - dataset no encontrado en datasets.yaml.
        3 - error de validacion de inputs.
        4 - reprojection error supero el umbral (degradado, no critico).
    """
    parser = argparse.ArgumentParser(
        description="Pipeline SfM multi-vista — genera cloud.ply y metrics.json."
    )
    parser.add_argument(
        "--dataset",
        required=True,
        help="Nombre del dataset declarado en data/datasets.yaml.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Carpeta de salida (por defecto: outputs/<dataset>/).",
    )
    parser.add_argument(
        "--detector",
        default="sift",
        choices=["sift", "orb"],
        help="Detector de features a usar (default: sift).",
    )
    parser.add_argument(
        "--lowe-ratio",
        type=float,
        default=0.75,
        help="Umbral del test de ratio de Lowe (default: 0.75).",
    )
    parser.add_argument(
        "--ransac-threshold",
        type=float,
        default=1.0,
        help="Umbral RANSAC en pixeles para la matriz fundamental (default: 1.0).",
    )
    parser.add_argument(
        "--min-matches",
        type=int,
        default=8,
        help="Minimo de matches validos por par de imagenes (default: 8).",
    )
    parser.add_argument(
        "--window",
        type=int,
        default=None,
        help="Ventana de matching entre imágenes (default: valor en sfm.py).",
    )
    parser.add_argument(
        "--iqr-factor",
        type=float,
        default=None,
        help="Factor IQR para filtro de outliers en la nube (default: valor en sfm.py).",
    )
    parser.add_argument(
        "--max-reproj-error",
        type=float,
        default=None,
        help="Error de reproyección máximo en px (default: valor en sfm.py).",
    )
    parser.add_argument(
        "--min-parallax",
        type=float,
        default=None,
        help="Paralaje mínimo en grados para aceptar un punto 3D (default: valor en sfm.py).",
    )
    parser.add_argument(
        "--n-features",
        type=int,
        default=None,
        help="Número de keypoints SIFT por imagen (default: 4000).",
    )
    args = parser.parse_args()

    from sfm_pipeline import sfm
    from sfm_pipeline.config import get_dataset, load_datasets_registry

    try:
        registry = load_datasets_registry("data/datasets.yaml")
        get_dataset(registry, args.dataset)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(3)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(2)

    try:
        result = sfm.run_pipeline(
            dataset_name=args.dataset,
            output_dir=args.output,
            detector=args.detector,
            lowe_ratio=args.lowe_ratio,
            ransac_threshold=args.ransac_threshold,
            min_matches=args.min_matches,
            n_features=args.n_features or 4000,
            window=args.window,
            iqr_factor=args.iqr_factor,
            max_reproj_error=args.max_reproj_error,
            min_parallax_deg=args.min_parallax,
        )
    except (ValueError, RuntimeError) as exc:
        print(f"ERROR de validacion: {exc}", file=sys.stderr)
        sys.exit(3)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR inesperado: {exc}", file=sys.stderr)
        sys.exit(1)

    rep_err = result["reprojection_error_mean"]
    print(
        f"Pipeline completado: {result['num_3d_points']} puntos 3D, "
        f"{result['num_images']} camaras registradas, "
        f"reprojection error = {rep_err:.2f} px"
    )

    if rep_err > 5.0:  # noqa: PLR2004
        print("AVISO: reprojection error > 5 px — resultado degradado.", file=sys.stderr)
        sys.exit(4)

    sys.exit(0)


if __name__ == "__main__":
    main()
