# Entrega 1 - 30 de abril de 2026

Hoja 1 (una pagina) que se sube a Canvas junto al link del repositorio.

## Checklist de avance funcional

- [x] Repositorio publico con estructura modular y `requirements.txt` instalable
- [x] Dataset 1 (objeto 360 grados) y dataset 2 (fachada) en `data/`
- [x] Deteccion SIFT y ORB corriendo sobre ambos datasets con visualizacion de keypoints
- [x] `geometry.py`: estimacion de F con `cv2.findFundamentalMat` + RANSAC validada en par sintetico con >= 60% de inliers
- [ ] Backend FastAPI con `POST /reconstruct` devolviendo `.ply` mock
- [ ] Frontend Three.js mostrando el `.ply` de prueba en el navegador
