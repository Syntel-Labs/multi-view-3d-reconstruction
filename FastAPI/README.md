# FastAPI + Three.js mock reconstruction

This project exposes a `POST /reconstruct` endpoint that accepts a ZIP file,
validates it, and returns a mock `.ply` point cloud. The frontend uploads the
ZIP and visualizes the returned `.ply` in the browser with Three.js.

## Run

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn backend.app.main:app --reload
```

Open `http://127.0.0.1:8000`.

## API behavior

- `POST /reconstruct`
- Form field: `archive`
- Accepts: `.zip`
- Returns: mock `mock-reconstruction.ply`

Example with `curl`:

```bash
curl -X POST ^
  -F "archive=@sample.zip" ^
  http://127.0.0.1:8000/reconstruct ^
  --output mock-reconstruction.ply
```

## Notes

- The backend currently ignores the ZIP contents after validation.
- Replace `build_mock_ply()` in `backend/app/mock_ply.py` with your real
  reconstruction pipeline when it is ready.
- The frontend imports Three.js from a CDN, so the browser needs internet
  access unless you vendor those files locally.
