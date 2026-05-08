from __future__ import annotations

import os
from pathlib import Path

import yaml


def get_required_env(name: str) -> str:
    """Leer una variable de entorno obligatoria o levantar error si no existe.

    Args:
        name: Nombre de la variable de entorno.

    Returns:
        Valor de la variable como cadena de texto.

    Raises:
        RuntimeError: Si la variable no esta definida en el entorno.
    """
    try:
        return os.environ[name]
    except KeyError:
        msg = f"Variable de entorno requerida no definida: {name}"
        raise RuntimeError(msg) from None


def load_datasets_registry(path: str | Path) -> dict:
    """Cargar el registro de datasets desde un archivo YAML.

    Args:
        path: Ruta al archivo datasets.yaml.

    Returns:
        Diccionario completo con la clave "datasets" y su lista de entradas.

    Raises:
        FileNotFoundError: Si el archivo no existe en la ruta indicada.
    """
    registry_path = Path(path)
    if not registry_path.exists():
        msg = f"No se encontro el archivo de registro: {registry_path}"
        raise FileNotFoundError(msg)

    with registry_path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_dataset(registry: dict, name: str) -> dict:
    """Buscar un dataset por nombre dentro del registro cargado.

    Args:
        registry: Diccionario cargado con load_datasets_registry; debe
            contener la clave "datasets" con una lista de entradas.
        name: Nombre del dataset a buscar (campo "name" de cada entrada).

    Returns:
        Diccionario con los datos del dataset encontrado.

    Raises:
        ValueError: Si no existe ningun dataset con el nombre indicado.
    """
    for dataset in registry.get("datasets", []):
        if dataset.get("name") == name:
            return dataset
    msg = f"Dataset '{name}' no encontrado en el registro."
    raise ValueError(msg)
