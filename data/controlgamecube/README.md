# Dataset gamecube

Mando de Consola Nintendo GameCube fotografiada en 360 grados como objeto pequeño con texturas y detalle.

## Metadata

* Fecha de captura: no disponible (sin EXIF)
* Capturado por: Mathew Cordero Aquino (22982)
* Dispositivo: no detectado (imágenes sin EXIF)
* Device id: unknown_device_01
* Cantidad de imagenes objetivo: 24
* Cantidad de imagenes capturadas: 78
* Resolucion: 478x850
* Solapamiento estimado: ≥ 60% (estimado por cantidad de imágenes)
* Iluminacion: uniforme, brillo promedio 141 (rango 129–151)
* Notas: dataset con baja resolución y sin metadatos EXIF; alta cantidad de imágenes borrosas (73/78 con baja nitidez); posible pérdida de calidad por compresión o captura en movimiento; color promedio BGR (141, 138, 145)

## Estructura

```text
data/gamecube/
├── README.md
├── intrinsics.json
```

## Validacion

```bash
make pipeline DATASET=gamecube
```

Cuando el smoke test pase, actualizar `status: validated` en `data/datasets.yaml`.
