"""CLI entrypoint del pipeline. Uso: python -m sfm_pipeline.cli --dataset <nombre>.

Contrato: docs/contracts/cli-sfm.md.
"""

import argparse


def main() -> None:
    """Parsear argumentos y delegar en sfm.run_pipeline."""
    parser = argparse.ArgumentParser(description="Pipeline SfM multi-vista")
    parser.add_argument("--dataset", required=True, help="Nombre del dataset en datasets.yaml")
    parser.add_argument("--output", default=None, help="Carpeta de salida (opcional)")
    parser.parse_args()
    raise NotImplementedError("Pendiente: invocar sfm.run_pipeline con los argumentos.")


if __name__ == "__main__":
    main()
