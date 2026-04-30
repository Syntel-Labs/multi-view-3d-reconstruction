# Contratos de interfaz

Acuerdos firmados el dia 1 que permiten que los 4 integrantes trabajen en paralelo sin bloqueo. Cada contrato define un schema de datos o de invocacion entre dos roles.

## Listado

| Contrato | Productor | Consumidor | Documento |
| :--- | :--- | :--- | :--- |
| Datasets | D | A, B | [`datasets.md`](datasets.md) |
| `matches.npz` | A | B | [`matches-npz.md`](matches-npz.md) |
| `intrinsics.json` | D | A, B | [`intrinsics-json.md`](intrinsics-json.md) |
| `cloud.ply` | B | C, D | [`cloud-ply.md`](cloud-ply.md) |
| `metrics.json` | B | C, D | [`metrics-json.md`](metrics-json.md) |
| CLI `sfm` | B | C | [`cli-sfm.md`](cli-sfm.md) |

## Reglas de cambio

- Un contrato se cambia con PR explicito que toque el `.md` correspondiente.
- El cambio requiere acuerdo de productor y consumidores antes del merge.
- Cualquier modificacion del schema implica bumping minimo en la version del contrato (campo `version` al inicio de cada documento).
