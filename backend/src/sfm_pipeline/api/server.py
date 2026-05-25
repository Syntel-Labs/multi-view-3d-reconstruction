"""Servidor FastAPI — pipeline SfM."""

import json
import traceback
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

app = FastAPI(title="mv3d-hartley", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

OUTPUTS_DIR = Path("outputs")


class ReconstructRequest(BaseModel):
    dataset: str
    detector: str = "sift"
    lowe_ratio: float = 0.72
    ransac_threshold: float = 1.0
    min_matches: int = 8
    window: int = 20
    iqr_factor: float = 2.0
    max_reproj_error: float = 8.0
    min_parallax: float = 0.01
    n_features: int = 4000


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/datasets")
def list_datasets() -> dict:
    from sfm_pipeline.config import load_datasets_registry

    try:
        registry = load_datasets_registry("data/datasets.yaml")
        datasets = registry.get("datasets", [])
        return {
            "datasets": [
                {
                    "name": d.get("name", ""),
                    "description": d.get("description", ""),
                    "status": d.get("status", "unknown"),
                    "expected_images": d.get("expected_images", 0),
                }
                for d in datasets
            ]
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/outputs/{dataset}/cloud.ply")
def get_cloud(dataset: str) -> FileResponse:
    ply_path = OUTPUTS_DIR / dataset / "cloud.ply"
    if not ply_path.exists():
        raise HTTPException(
            status_code=404, detail=f"cloud.ply no encontrado para '{dataset}'"
        )
    return FileResponse(str(ply_path), media_type="application/octet-stream")


@app.get("/outputs/{dataset}/metrics")
def get_metrics(dataset: str) -> dict:
    metrics_path = OUTPUTS_DIR / dataset / "metrics.json"
    if not metrics_path.exists():
        raise HTTPException(
            status_code=404, detail=f"metrics.json no encontrado para '{dataset}'"
        )
    return json.loads(metrics_path.read_text())


@app.post("/reconstruct")
def reconstruct(req: ReconstructRequest) -> dict:
    from sfm_pipeline import sfm
    from sfm_pipeline.config import get_dataset, load_datasets_registry

    try:
        registry = load_datasets_registry("data/datasets.yaml")
        get_dataset(registry, req.dataset)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    try:
        result = sfm.run_pipeline(
            dataset_name=req.dataset,
            detector=req.detector,
            lowe_ratio=req.lowe_ratio,
            ransac_threshold=req.ransac_threshold,
            min_matches=req.min_matches,
            n_features=req.n_features,
            window=req.window,
            iqr_factor=req.iqr_factor,
            max_reproj_error=req.max_reproj_error,
            min_parallax_deg=req.min_parallax,
        )
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=422, detail=f"{type(exc).__name__}: {exc}")
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}",
        )

    result["dataset_id"] = req.dataset
    return result
