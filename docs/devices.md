# Dispositivos de captura

Catalogo de dispositivos (telefonos y, eventualmente, camaras dedicadas) usados para capturar los datasets del proyecto. Cada dataset registrado en `data/datasets.yaml` referencia un dispositivo de esta lista mediante el campo `device_id`. Se mantiene actualizado a medida que se incorporan dispositivos nuevos al equipo.

## Como llenar

- `id` en kebab-case, descriptivo y unico (incluir nombre del integrante si dos personas usan el mismo modelo): `pixel-7-josue`, `iphone-13-maria`, `s23-luis`.
- Si el mismo telefono se usa con dos modos de captura distintos (auto vs profesional), registrar dos entradas con sufijo: `pixel-7-josue-auto`, `pixel-7-josue-pro`.
- Imagenes deben preservar EXIF para extraer la focal automaticamente. Si EXIF se pierde (por ejemplo al pasar por WhatsApp o iCloud comprimido), documentarlo y rellenar `intrinsics.json` manualmente.

## Plantilla por dispositivo

```markdown
### {id}

- Modelo: {marca y modelo, ej. Google Pixel 7}
- Tipo: {telefono | camara dedicada}
- Sistema operativo: {Android 14 | iOS 17 | ...}
- Resolucion de captura: {WxH px}
- Sensor (si conocido): {ancho en mm}
- Focal EXIF (si conocido): {focal en mm}
- Lente usado: {principal | gran angular | tele}
- Modo de captura: {automatico | manual | profesional | RAW}
- Formato: {JPG | HEIC | DNG}
- Notas: {estabilizacion, recortes, postprocesado del fabricante, etc.}
```

## Dispositivos registrados

### pendiente

- Modelo: pendiente
- Tipo: telefono
- Sistema operativo: pendiente
- Resolucion de captura: pendiente
- Sensor: pendiente
- Focal EXIF: pendiente
- Lente usado: pendiente
- Modo de captura: pendiente
- Formato: pendiente
- Notas: pendiente

## Construccion de K desde EXIF del telefono

La mayoria de los telefonos exponen `FocalLength` y `FocalLengthIn35mmFilm` en los metadatos EXIF. Para obtener la focal en pixeles:

$$
f_{px} \approx f_{mm} \cdot \frac{W}{s_{mm}}
$$

Donde $W$ es el ancho de la imagen en pixeles y $s_{mm}$ es el ancho fisico del sensor. Si el dispositivo no expone $s_{mm}$ directamente, se puede aproximar con `FocalLengthIn35mmFilm` y la formula equivalente:

$$
f_{px} \approx f_{35mm} \cdot \frac{W}{36}
$$

Esto da una estimacion suficiente para el pipeline core; el refinamiento final lo absorbe el bundle adjustment.

## Referencias

- Contrato: [`contracts/intrinsics-json.md`](contracts/intrinsics-json.md).
- Contrato: [`contracts/datasets.md`](contracts/datasets.md).
