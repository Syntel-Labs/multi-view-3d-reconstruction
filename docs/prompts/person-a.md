# Log de prompts - Persona A

## 2026-05-07 - Implementar matching en ventana ampliada (windowed matching)

- Herramienta: Claude Sonnet (claude.ai/code o CLI)
- URL herramienta:
- URL origen:
- Modulo / area: `backend/src/sfm_pipeline/matching.py`, `backend/src/sfm_pipeline/sfm.py`
- Prompt: |
    Contexto del proyecto: pipeline SfM incremental en Python con OpenCV.
    El repositorio es https://github.com/Syntel-Labs/multi-view-3d-reconstruction.

    Problema actual: el pipeline solo matchea pares consecutivos (i, i+1).
    Con 78 imagenes del dataset controlgamecube solo se registran 18 camaras (23 %)
    porque cuando un par falla no hay fallback para recuperar la cadena.

    Lo que necesito implementar:

    1. En `backend/src/sfm_pipeline/matching.py` agregar la funcion:

       def match_windowed(
           desc_arrays: list[np.ndarray],
           detector: str = "sift",
           ratio: float = 0.75,
           window: int = 3,
       ) -> dict[tuple[int, int], np.ndarray]:

       - Debe matchear cada imagen i contra las imagenes i+1, i+2, ..., i+window
         (sin salirse del rango de la lista).
       - Para cada par (i, j) retornar un array (M, 2) int32 con los indices de
         keypoints de cada imagen que pasaron el Lowe ratio test, identico al
         formato que ya usa matches_pairs en sfm.py.
       - Usar la funcion match_descriptors ya existente en el mismo archivo para
         no duplicar logica.
       - Tipado completo, docstring en espanol, manejo de ValueError si hay menos
         de 2 imagenes.

    2. En `backend/src/sfm_pipeline/sfm.py`, en la seccion "4. Matching de pares
       consecutivos" (linea ~114), reemplazar el bucle actual por una llamada a
       match_windowed con window=3 (parametrizable desde run_pipeline).

       El resto del pipeline consume matches_pairs como list[np.ndarray] para
       pares consecutivos; la nueva estructura sera dict[tuple[int,int], np.ndarray].
       Ajusta los accesos en las secciones de geometria del par inicial y del
       sliding window para leer del dict por clave (i, j) en lugar de indice.

    3. Agregar el parametro `match_window: int = 3` a la firma de run_pipeline
       en sfm.py y propagarlo a match_windowed.

    Restricciones:
  - No romper la firma publica de run_pipeline (parametros nuevos deben tener
      default para mantener compatibilidad con el CLI existente).
  - Seguir el estandar ruff del proyecto (ruff.toml en backend/).
  - Sin comentarios que expliquen el que, solo el por que si es no obvio.
  - Tipado obligatorio en parametros y retorno.

    Lee los archivos antes de editar. Corre `ruff check backend/` al terminar.

- Resultado: pendiente de ejecutar
- Uso: adaptado
- Justificacion: el cambio afecta dos modulos con logica interdependiente
  (matching y sfm); usar IA permite generar la refactorizacion de forma consistente
  y verificar que el dict de pares se propaga correctamente a todas las secciones
  del pipeline en una sola pasada.
