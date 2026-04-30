# Contrato - Datasets

- Version: 0.1.0
- Productor: Persona D
- Consumidores: Persona A, Persona B

Define la estructura de cada dataset y el registro central en `data/datasets.yaml`.

## Estructura por dataset

```text
data/<name>/
├── images/             # fotografias .jpg/.png con EXIF intacto
├── intrinsics.json     # K aproximada del dataset (ver intrinsics-json.md)
└── README.md           # descripcion, fecha, condiciones y dispositivo usado
```

## Registro central

Archivo `data/datasets.yaml`. Schema:

```yaml
datasets:
  - name: <kebab-case>            # obligatorio, igual al nombre de la subcarpeta
    description: <texto>          # obligatorio
    path: data/<name>             # obligatorio, ruta relativa al repo
    expected_images: <int>        # obligatorio
    intrinsics: data/<name>/intrinsics.json   # obligatorio
    captured_by: <A|B|C|D>        # obligatorio
    capture_date: <YYYY-MM-DD>    # vacio si pending
    notes: <texto libre>          # opcional
    status: pending | captured | validated   # obligatorio
```

## Reglas

- `name` en kebab-case sin acentos.
- Las imagenes deben preservar EXIF para extraer la focal y construir `K`. Los telefonos suelen incluir `FocalLength` y `FocalLengthIn35mmFilm`; servicios como WhatsApp e iCloud comprimido pueden destruir estos campos.
- Si el dispositivo no expone EXIF (o se perdio en transito), documentarlo en el README del dataset y rellenar `intrinsics.json` manualmente.
- Cada dataset declara el `device_id` del dispositivo usado; la lista completa de dispositivos vive en [`docs/devices.md`](../devices.md).
- `status: validated` solo cuando el dataset paso un smoke test del pipeline (`make pipeline DATASET=<name>` corrio sin errores y produjo `cloud.ply`).

## Formato del `data/<name>/README.md`

```markdown
# Dataset {name}

- Fecha de captura: YYYY-MM-DD
- Capturado por: {iniciales}
- Dispositivo: {modelo, ej. Google Pixel 7}
- Device id: {referencia al catalogo en docs/devices.md}
- Cantidad de imagenes: {N}
- Resolucion: {WxH}
- Solapamiento estimado: {porcentaje}
- Iluminacion: {natural|artificial|mixta}
- Notas: ...
```
