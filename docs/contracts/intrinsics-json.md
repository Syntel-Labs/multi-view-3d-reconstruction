# Contrato - intrinsics.json

- Version: 0.2.0
- Productor: Persona D (genera) / Persona B (consume al construir K)
- Consumidores: Persona A, Persona B

Define la matriz intrinseca aproximada del dataset. El campo `device_id` apunta al dispositivo del catalogo en [`docs/devices.md`](../devices.md) (telefono o camara) usado para capturar las fotos.

## Schema

```json
{
  "device_id": "string",
  "device_model": "string",
  "image_width": 0,
  "image_height": 0,
  "focal_length_px": 0.0,
  "principal_point_px": [0.0, 0.0],
  "sensor_width_mm": 0.0,
  "exif_focal_length_mm": 0.0,
  "exif_focal_length_35mm": 0.0,
  "notes": "string"
}
```

## Reglas

- `device_id` debe coincidir con un id registrado en `docs/devices.md`.
- `device_model` se copia del catalogo para que el JSON sea autocontenido (util si se borra `devices.md` por error).
- `focal_length_px` se calcula como $f_{px} \approx f_{mm} \cdot W / s_{mm}$. Si el dispositivo no expone `sensor_width_mm`, usar la aproximacion via 35 mm: $f_{px} \approx f_{35mm} \cdot W / 36$.
- Si EXIF se perdio (compresion de WhatsApp / iCloud), llenar `focal_length_px` manualmente y dejar `exif_focal_length_mm` y `exif_focal_length_35mm` en `0.0`. Documentarlo en `notes`.
- `principal_point_px` por defecto es el centro de la imagen: $(W/2, H/2)$.

## Construccion de K

$$
K = \begin{bmatrix}
f_{px} & 0 & c_x \\
0 & f_{px} & c_y \\
0 & 0 & 1
\end{bmatrix}
$$
