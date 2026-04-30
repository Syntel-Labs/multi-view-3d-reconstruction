# Dataset other

Dataset secundario, pendiente de definir. Candidatos: fachada arquitectonica o escena interior.

## Metadata

- Fecha de captura: pendiente
- Capturado por: D
- Dispositivo: pendiente
- Device id: pendiente (registrar en `docs/devices.md`)
- Cantidad de imagenes objetivo: 10
- Resolucion: pendiente
- Solapamiento estimado: pendiente
- Iluminacion: pendiente
- Notas: renombrar la carpeta cuando se decida el sujeto y actualizar `data/datasets.yaml`.

## Estructura

```text
data/other/
├── README.md
├── intrinsics.json
└── images/             # fotografias .jpg con EXIF intacto
```

## Validacion

```bash
make pipeline DATASET=other
```

Cuando el smoke test pase, actualizar `status: validated` en `data/datasets.yaml`.
