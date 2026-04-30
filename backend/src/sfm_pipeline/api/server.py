"""Servidor FastAPI que expone el pipeline SfM al frontend.

Contrato: docs/contracts/cli-sfm.md.
"""

from fastapi import FastAPI

app = FastAPI(title="mv3d-hartley", version="0.1.0")


@app.get("/health")
def health() -> dict:
    """Probe de liveness del servicio."""
    return {"status": "ok"}


@app.post("/reconstruct")
def reconstruct() -> dict:
    """Endpoint principal de reconstruccion (pendiente).

    Recibira un ZIP de imagenes o un nombre de dataset registrado y devolvera la ruta
    relativa al cloud.ply generado mas las metricas del job.
    """
    raise NotImplementedError("Pendiente: integrar con sfm.run_pipeline.")
