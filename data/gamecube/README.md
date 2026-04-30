# Dataset gamecube

Consola Nintendo GameCube fotografiada en 360 grados como objeto pequeno con texturas y detalle.

## Metadata

- Fecha de captura: pendiente
- Capturado por: D
- Dispositivo: pendiente
- Device id: pendiente (registrar en `docs/devices.md`)
- Cantidad de imagenes objetivo: 24
- Resolucion: pendiente
- Solapamiento estimado: $\geq 60\%$
- Iluminacion: pendiente
- Notas: pendiente

## Estructura

```text
data/gamecube/
├── README.md
├── intrinsics.json
└── images/             # fotografias .jpg con EXIF intacto
```

## Validacion

```bash
make pipeline DATASET=gamecube
```

Cuando el smoke test pase, actualizar `status: validated` en `data/datasets.yaml`.
