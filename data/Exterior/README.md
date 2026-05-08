
# Dataset exterior

Fachada arquitectónica exterior.

## Metadata

- Fecha de captura: pendiente
- Capturado por: D
- Dispositivo: No detectado (sin EXIF)
- Device id: pendiente (registrar en `docs/devices.md`)
- Cantidad de imágenes objetivo: 20-30
- Cantidad de imágenes actuales: 300 (requiere filtrado)
- Resolución: 478x850 px (uniforme)
- Solapamiento estimado: pendiente
- Iluminación: brillo promedio 101.37 (rango 73–127)
- Notas: 100 imágenes borrosas estimadas (nitidez < umbral).
  Sin EXIF detectado — B debe aproximar K manualmente.
  Filtrar a 20-30 imágenes nítidas antes de correr el pipeline.

## Estructura

​```text
data/exterior/
├── README.md
├── intrinsics.json
└── images/             # fotografias .jpg con EXIF intacto
​```

## Validacion

​```bash
make pipeline DATASET=exterior
​```

Cuando el smoke test pase, actualizar `status: validated` en `data/datasets.yaml`.
```

---

