from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import subprocess

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

class PipelineArgs(BaseModel):
    dataset: str
    detector: str = "sift"
    lowe_ratio: float = 0.75
    ransac_threshold: float = 1.0
    min_matches: int = 8
    window: int = 20
    iqr_factor: float = 2.0
    max_reproj_error: float = 8.0
    min_parallax: float = 0.01
    n_features: int = 4000

@app.post("/api/run")
def run_pipeline(args: PipelineArgs):
    command = [
        "python", "-m", "sfm_pipeline.cli",
        "--dataset", args.dataset,
        "--detector", args.detector,
        "--lowe-ratio", str(args.lowe_ratio),
        "--ransac-threshold", str(args.ransac_threshold),
        "--min-matches", str(args.min_matches),
        "--window", str(args.window),
        "--iqr-factor", str(args.iqr_factor),
        "--max-reproj-error", str(args.max_reproj_error),
        "--min-parallax", str(args.min_parallax),
        "--n-features", str(args.n_features)
    ]
    
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise HTTPException(status_code=500, detail=result.stderr)
        
    return {"url": f"http://localhost:8000/outputs/{args.dataset}/cloud.ply"}
