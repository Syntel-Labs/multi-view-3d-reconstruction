# backend/scripts/

Scripts Python de uso unico (experimentos, sanity checks, utilidades manuales). No son parte del pipeline final; sirven como referencia para implementar los modulos en `backend/src/sfm_pipeline/`.

## Listado

| Script | Proposito | Origen |
| :--- | :--- | :--- |
| `orb_test.py` | Pipeline minimo de ORB + BFMatcher + Lowe ratio sobre dos imagenes. Sirve de referencia para `features.py` y `matching.py` (Persona A). | Experimento inicial. |
