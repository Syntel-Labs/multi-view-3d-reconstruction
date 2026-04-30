"""Carga de configuracion desde variables de entorno y datasets.yaml.

Centraliza el acceso a rutas y parametros del proyecto. Sin valores por defecto via `or` o
similar: si una variable obligatoria falta, se levanta un error explicito
"""


def get_required_env(name: str) -> str:
    """Leer una variable de entorno obligatoria o levantar error si no existe.

    Args:
        name: Nombre de la variable.

    Returns:
        Valor de la variable.

    Raises:
        RuntimeError: Si la variable no esta definida.
    """
    raise NotImplementedError("Pendiente: lectura desde os.environ con validacion.")


def load_datasets_registry(path: str) -> dict:
    """Cargar el registro de datasets desde data/datasets.yaml.

    Args:
        path: Ruta al archivo YAML.

    Returns:
        Diccionario con la lista de datasets disponibles.
    """
    raise NotImplementedError("Pendiente: parseo con pyyaml + validacion del schema.")
