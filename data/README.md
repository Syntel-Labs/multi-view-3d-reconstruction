# data/

Carpeta de datasets de entrada. Cada dataset vive en su propia subcarpeta y queda registrado en `datasets.yaml`. El contenido binario (imagenes) **no se versiona**.

## Estructura por dataset

```text
data/
├── datasets.yaml
├── README.md
└── <dataset-name>/
    ├── images/             # fotografias .jpg/.png con EXIF intacto
    ├── intrinsics.json     # K aproximada del dataset
    └── README.md           # descripcion del dataset y condiciones de captura
```

## Contrato

Definicion completa en `docs/contracts/datasets.md`.

- `name` en kebab-case ingles, igual al nombre de la subcarpeta.
- Imagenes con EXIF para extraer focal y construir `K`. La mayoria de telefonos exponen `FocalLength` y `FocalLengthIn35mmFilm`; al enviarlas por WhatsApp / iCloud comprimido se pueden perder.
- Cada dataset declara el dispositivo de captura mediante `device_id` apuntando a [`docs/devices.md`](../docs/devices.md).
- Si el dispositivo no expone EXIF (o se perdio en transito), documentarlo en el README del dataset y rellenar `intrinsics.json` manualmente.

## Anadir un dataset nuevo

1. Crear la carpeta `data/<name>/images/` y volcar las fotos.
2. Generar `intrinsics.json` desde EXIF (script pendiente) o llenarlo manualmente.
3. Crear `data/<name>/README.md` con descripcion, fecha y condiciones de captura.
4. Anadir la entrada en `datasets.yaml` con `status: captured`.
5. Validar el dataset corriendo el pipeline: `make pipeline DATASET=<name>`.
6. Cuando pase el smoke test, actualizar `status: validated`.

## Versionado

Las imagenes y archivos binarios estan en `.gitignore`. Solo se versionan:

- `datasets.yaml`
- `README.md` global (este archivo)
- `data/<name>/README.md` de cada dataset
- `data/<name>/intrinsics.json` (texto, util para reproducibilidad)
