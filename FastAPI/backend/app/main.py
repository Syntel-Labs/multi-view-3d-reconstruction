from __future__ import annotations

import io
import zipfile
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles

from .mock_ply import build_mock_ply

app = FastAPI(title="Mock Reconstruction API")
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", response_class=FileResponse)
async def index() -> FileResponse:
    return FileResponse(static_dir / "index.html")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/reconstruct")
async def reconstruct(archive: UploadFile = File(...)) -> Response:
    if not archive.filename:
        raise HTTPException(status_code=400, detail="Missing ZIP filename.")

    if not archive.filename.lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="The uploaded file must be a .zip.")

    content = await archive.read()
    if not content:
        raise HTTPException(status_code=400, detail="The uploaded ZIP is empty.")

    try:
        with zipfile.ZipFile(io.BytesIO(content)) as zipped:
            filenames = [name for name in zipped.namelist() if not name.endswith("/")]
    except zipfile.BadZipFile as exc:
        raise HTTPException(status_code=400, detail="Invalid ZIP file.") from exc

    if not filenames:
        raise HTTPException(
            status_code=400,
            detail="The ZIP does not contain any files to reconstruct.",
        )

    ply_bytes = build_mock_ply()
    headers = {
        "Content-Disposition": 'attachment; filename="mock-reconstruction.ply"',
        "X-Source-File-Count": str(len(filenames)),
    }
    return Response(
        content=ply_bytes,
        media_type="application/octet-stream",
        headers=headers,
    )

