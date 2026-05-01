"""Utilidades de logging y debugging reutilizables para todos los modulos del pipeline.

Los logs se escriben simultaneamente a stdout y, si se indica log_file, a un archivo
en outputs/logs/ que persiste entre ejecuciones.

Uso basico:
    from sfm_pipeline.debug import PipelineLogger

    log = PipelineLogger("geometry", log_file="outputs/logs/geometry.log")
    log.section("Estimando F")
    log.param("n_puntos", 300)
    log.stats("Inliers", {"count": 216, "ratio": 0.72})
    log.matrix("F", F)
    log.warn("ratio bajo")
    log.ok("F estimada")
    log.summary({"Inlier ratio": (0.72, True)})
"""

from __future__ import annotations

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np


def _build_file_handler(log_file: str, log_level: int) -> logging.FileHandler:
    """Crear un FileHandler que escribe al archivo indicado (crea la carpeta si no existe)."""
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    handler = logging.FileHandler(log_file, encoding="utf-8")
    handler.setLevel(log_level)
    handler.setFormatter(logging.Formatter("%(asctime)s\t%(levelname)s\t%(message)s"))
    return handler


class PipelineLogger:
    """Logger estructurado para un modulo del pipeline SfM.

    Escribe a stdout y opcionalmente a un archivo de log persistente.

    Args:
        module:    nombre del modulo (prefijo visible en cada linea).
        verbose:   si False, todos los metodos son no-op excepto warn/fail.
        log_level: nivel de logging de Python (DEBUG, INFO, WARNING...).
        log_file:  ruta al archivo de log. Si es None no se escribe a disco.
                   Usar "auto" para generar outputs/logs/<modulo>_<timestamp>.log
                   automaticamente.
    """

    def __init__(
        self,
        module: str,
        verbose: bool = True,
        log_level: int = logging.DEBUG,
        log_file: str | None = None,
    ) -> None:
        self.module = module
        self.verbose = verbose
        self.log_level = log_level
        self._logger = logging.getLogger(f"sfm_pipeline.{module}")
        self._logger.setLevel(log_level)
        self._file_path: str | None = None

        if log_file is not None:
            if log_file == "auto":
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                log_file = f"outputs/logs/{module}_{ts}.log"
            handler = _build_file_handler(log_file, log_level)
            self._logger.addHandler(handler)
            self._file_path = log_file
            # Escribir cabecera en el archivo para identificar la sesion
            self._logger.log(log_level, "=" * 56)
            self._logger.log(log_level, "\tSESION\t%s\tmodulo=%s", datetime.now().isoformat(), module)
            self._logger.log(log_level, "=" * 56)

    @property
    def log_file(self) -> str | None:
        """Ruta del archivo de log activo, o None si no hay."""
        return self._file_path

    # ------------------------------------------------------------------
    # API publica
    # ------------------------------------------------------------------

    def section(self, title: str) -> None:
        """Separador de seccion con titulo."""
        if not self.verbose:
            return
        sep = "=" * 56
        self._emit(f"\n{sep}")
        self._emit(f"\t{self.module.upper()} | {title}")
        self._emit(sep)

    def info(self, msg: str, *args: Any) -> None:
        """Mensaje informativo general."""
        self._emit(f"\t[{self.module}] {msg}", *args)

    def param(self, name: str, value: Any, unit: str = "") -> None:
        """Loguear el valor de un parametro de entrada."""
        suffix = f" {unit}" if unit else ""
        self._emit(f"\t  {name:<24} {value}{suffix}")

    def stats(self, label: str, values: dict[str, Any]) -> None:
        """Tabla de estadisticas: una entrada por linea con tabulacion."""
        if not self.verbose:
            return
        self._emit(f"\t[{self.module}] {label}:")
        for k, v in values.items():
            if isinstance(v, float):
                self._emit(f"\t\t{k:<28} {v:.6f}")
            else:
                self._emit(f"\t\t{k:<28} {v}")

    def matrix(self, name: str, M: np.ndarray) -> None:
        """Matriz alineada con tabulacion por columna."""
        if not self.verbose:
            return
        self._emit(f"\t[{self.module}] {name}:")
        for row in M:
            self._emit("\t\t" + "\t".join(f"{v:+.6f}" for v in row))

    def vector(self, name: str, v: np.ndarray, precision: int = 6) -> None:
        """Vector fila con tabulacion."""
        if not self.verbose:
            return
        fmt = "\t".join(f"{x:+.{precision}f}" for x in np.asarray(v).ravel())
        self._emit(f"\t[{self.module}] {name}: {fmt}")

    def warn(self, msg: str, *args: Any) -> None:
        """Advertencia: visible incluso con verbose=False, siempre va al archivo."""
        text = msg % args if args else msg
        self._logger.warning("\t[%s] ADVERTENCIA: %s", self.module, text)
        print(f"\t[{self.module}] ADVERTENCIA: {text}")

    def ok(self, msg: str, *args: Any) -> None:
        """Mensaje de exito."""
        self._emit(f"\t[{self.module}] OK: {msg}", *args)

    def fail(self, msg: str, *args: Any) -> None:
        """Fallo: visible incluso con verbose=False, siempre va al archivo."""
        text = msg % args if args else msg
        self._logger.error("\t[%s] FALLO: %s", self.module, text)
        print(f"\t[{self.module}] FALLO: {text}")

    def summary(self, checks: dict[str, tuple[Any, bool]]) -> bool:
        """Resumen final con estado OK/FALLO por criterio.

        Args:
            checks: {descripcion: (valor, cumple)}.

        Returns:
            True si todos los criterios se cumplen.
        """
        all_ok = all(ok for _, ok in checks.values())
        if not self.verbose:
            return all_ok
        sep = "-" * 56
        self._emit(f"\n{sep}")
        self._emit(f"\tRESUMEN {self.module.upper()}")
        self._emit(sep)
        for desc, (val, ok) in checks.items():
            status = "OK" if ok else "FALLO"
            if isinstance(val, float):
                self._emit(f"\t  {desc:<32} {val:.4f}\t{status}")
            else:
                self._emit(f"\t  {desc:<32} {val}\t{status}")
        self._emit(sep + "\n")
        return all_ok

    # ------------------------------------------------------------------
    # Helpers internos
    # ------------------------------------------------------------------

    def _emit(self, msg: str, *args: Any) -> None:
        if not self.verbose:
            return
        text = msg % args if args else msg
        self._logger.log(self.log_level, text)
        print(text)
