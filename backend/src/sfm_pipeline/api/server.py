"""Servidor FastAPI que expone el pipeline SfM al frontend.

Contrato: docs/contracts/cli-sfm.md.
"""

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

app = FastAPI(title="mv3d-hartley", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

OUTPUTS_DIR = Path("outputs")


@app.get("/health")
def health() -> dict:
    """Probe de liveness del servicio."""
    return {"status": "ok"}


@app.get("/outputs/{dataset}/cloud.ply")
def get_cloud(dataset: str) -> FileResponse:
    """Servir la nube de puntos PLY generada por el pipeline."""
    ply_path = OUTPUTS_DIR / dataset / "cloud.ply"
    if not ply_path.exists():
        raise HTTPException(status_code=404, detail=f"cloud.ply no encontrado para '{dataset}'")
    return FileResponse(str(ply_path), media_type="application/octet-stream")


@app.get("/outputs/{dataset}/metrics")
def get_metrics(dataset: str) -> dict:
    """Servir las metricas JSON del pipeline."""
    import json
    metrics_path = OUTPUTS_DIR / dataset / "metrics.json"
    if not metrics_path.exists():
        raise HTTPException(status_code=404, detail=f"metrics.json no encontrado para '{dataset}'")
    return json.loads(metrics_path.read_text())


@app.post("/reconstruct")
def reconstruct() -> dict:
    """Endpoint principal de reconstruccion (pendiente).

    Recibira un ZIP de imagenes o un nombre de dataset registrado y devolvera la ruta
    relativa al cloud.ply generado mas las metricas del job.
    """
    raise NotImplementedError("Pendiente: integrar con sfm.run_pipeline.")
