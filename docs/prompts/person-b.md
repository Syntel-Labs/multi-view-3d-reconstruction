# Log de prompts - Persona B

## 2026-05-07 - Diagnostico y fix del cascade failure en registro de camaras

- Herramienta: Claude Sonnet (Claude Code CLI)
- URL herramienta:
- URL origen:
- Modulo / area: `backend/src/sfm_pipeline/sfm.py`
- Prompt: |
    El pipeline SfM registra solo 9-10 camaras de 78 en el dataset controlgamecube.
    El sliding window en sfm.py itera sobre range(i-2, max(-1, i-1-lookback), -1)
    para buscar correspondencias 3D-2D. Cuando los frames 10-20 fallan, el frame 21
    no encuentra camaras registradas en esa ventana aunque haya camaras registradas
    antes del frame 10.

    Diagnostica la causa raiz e implementa el fix: el sliding window debe iterar
    sobre camaras efectivamente registradas (camera_rs[j] is not None), no sobre
    indices de frame. Manten el mismo lookback maximo. Corre el pipeline despues
    del fix y reporta cuantas camaras se registran ahora.
- Resultado: fix aplicado en sfm.py lineas ~200-220; camaras registradas pasaron
  de 9-10 a 18 para controlgamecube.
- Uso: adaptado
- Justificacion: el bug era sutil — la ventana usaba indices de frame pero debia
  usar indices de camaras registradas; la IA identifico el patron en menos tiempo
  del que tomaria un debug manual con prints.

---

## 2026-05-07 - Filtro IQR para eliminar outliers de la nube de puntos

- Herramienta: Claude Sonnet (Claude Code CLI)
- URL herramienta:
- URL origen:
- Modulo / area: `backend/src/sfm_pipeline/sfm.py`
- Prompt: |
    La nube de puntos exportada tiene coordenadas Z del orden de 8.9e14 en algunos
    puntos (triangulaciones degeneradas). El visor Three.js muestra pantalla negra
    porque boundingBox.getCenter() se jala a esos extremos.

    Agrega un filtro IQR en sfm.py antes de exportar el PLY: calcular q25 y q75
    por coordenada, definir inlier_mask con margen 3*IQR, y filtrar pts3d_all.
    Reporta cuantos puntos se eliminan.
- Resultado: filtro IQR agregado antes del export en sfm.py; se eliminaron 35
  outliers (438 -> 403 puntos) en controlgamecube.
- Uso: literal
- Justificacion: el patron IQR es estandar pero requiere manejar el caso iqr~0
  (coordenadas constantes) que sin IA se olvida facilmente.

---

## 2026-05-07 - Implementar endpoints HTTP para cloud.ply y metrics

- Herramienta: Claude Sonnet (Claude Code CLI)
- URL herramienta:
- URL origen:
- Modulo / area: `backend/src/sfm_pipeline/api/server.py`
- Prompt: |
    El backend FastAPI en server.py solo tiene GET /health. Necesito dos endpoints
    nuevos para que el frontend pueda consumir las salidas del pipeline:

  - GET /outputs/{dataset}/cloud.ply — devuelve el archivo binario PLY con
      FileResponse y media_type application/octet-stream.
  - GET /outputs/{dataset}/metrics — lee metrics.json y devuelve el dict.

    Agrega tambien CORS middleware con allow_origins=["*"] y allow_methods=["GET"]
    para que el visor HTML pueda llamar desde file:// o localhost:5175.
    El directorio base de outputs esta en OUTPUTS_DIR definido en config.py.
    Manten ruff limpio.
- Resultado: dos endpoints agregados con CORS; FileResponse sirve el PLY
  correctamente como binario.
- Uso: adaptado
- Justificacion: la combinacion FileResponse + CORS tiene varios parametros
  no obvios (media_type, headers de CORS para requests con credenciales); la IA
  genero el patron correcto en una pasada sin necesidad de consultar la doc de
  Starlette/FastAPI.

---

## 2026-05-07 - Diagnostico de pantalla negra en visor Three.js

- Herramienta: Claude Sonnet (Claude Code CLI)
- URL herramienta:
- URL origen:
- Modulo / area: `outputs/controlgamecube/test_viewer.html`
- Prompt: |
    El visor Three.js muestra pantalla negra para el dataset controlgamecube pero
    funciona para apple_co3d. El PLY ya tiene outliers eliminados. Diagnostica por
    que la nube no se ve.

    Contexto: la camara se posiciona a span*2.2 donde span es el rango 5-95 de la
    nube. Para controlgamecube el span es ~862 unidades, por lo que la camara queda
    a ~1896. El far plane de PerspectiveCamera esta en 1000.
- Resultado: se identifico que far=1000 clippeaba todo para span grande; se cambio
  a far=1e7. La nube aparecio correctamente.
- Uso: adaptado
- Justificacion: el problema era una interaccion entre el span real de los datos
  y el frustum de Three.js; sin conocer el span exacto del dataset es dificil
  diagnosticarlo solo con inspeccion visual.

---

## 2026-05-07 - Integracion del dataset CO3D apple con intrinsics en formato NDC

- Herramienta: Claude Sonnet (Claude Code CLI)
- URL herramienta:
- URL origen: https://github.com/facebookresearch/co3d
- Modulo / area: `data/apple_co3d/intrinsics.json`
- Prompt: |
    El dataset CO3D de Meta almacena las intrinsics en coordenadas NDC de PyTorch3D,
    no en pixeles. El campo focal_length es [fx_ndc, fy_ndc] y principal_point es
    [px_ndc, py_ndc] con origen en el centro de la imagen.

    Para una imagen de 707x1259 px con focal_length=[3.7981, 3.7981] y
    principal_point=[-0.0000, 0.0000], calcula fx_px, fy_px, cx_px, cy_px usando
    la formula de PyTorch3D: fx_px = focal_length[0] * min(H,W) / 2.
    Genera el intrinsics.json con el schema del proyecto.
- Resultado: intrinsics.json generado con focal_length_px=1342.99,
  principal_point_px=[353.5, 629.5] para la imagen 707x1259.
- Uso: literal
- Justificacion: la conversion NDC->pixeles de PyTorch3D tiene un factor min(H,W)/2
  no documentado de forma prominente; buscarlo manualmente en el codigo fuente de
  CO3D habria tomado considerablemente mas tiempo.
