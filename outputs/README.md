# outputs/

Salidas generadas por el pipeline SfM. **No se versionan** (estan en `.gitignore`).

## Estructura

```text
outputs/
└── <dataset-name>/
    ├── cloud.ply
    ├── metrics.json
    └── logs/
        └── YYYYMMDD_hhmmss.log
```

## Contratos

- `cloud.ply`: `docs/contracts/cloud-ply.md`.
- `metrics.json`: `docs/contracts/metrics-json.md`.

## Limpieza

```bash
rm -rf outputs/<dataset-name>
```

O directamente desde host: `make clean` no toca `outputs/`; debe limpiarse manual.
